# Python 2/3 compatibility
from __future__ import print_function
import numpy as np
import cv2 as cv
import imutils, time
import os
import sys
PY3 = sys.version_info[0] == 3

if PY3:
    xrange = range

min_area = 15000
max_skew = 0.45
image_format = "png"
out_path = "out"+str(time.time())

def angle_cos(p0, p1, p2):
    d1, d2 = (p0-p1).astype('float'), (p2-p1).astype('float')
    return abs( np.dot(d1, d2) / np.sqrt( np.dot(d1, d1)*np.dot(d2, d2) ) )


def find_squares(img):
    img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    img = cv.GaussianBlur(img, (5, 5), 0)
    squares = []
    for gray in cv.split(img):
        for thrs in xrange(0, 255, 26):
            if thrs == 0:
                bin = cv.Canny(gray, 0, 50, apertureSize=5)
                bin = cv.dilate(bin, None)
            else:
                _retval, bin = cv.threshold(gray, thrs, 255, cv.THRESH_BINARY)
            bin = cv.findContours(bin, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
            contours = imutils.grab_contours(bin)
            for cnt in contours:
                cnt_len = cv.arcLength(cnt, True)
                cnt = cv.approxPolyDP(cnt, 0.02*cnt_len, True)
                if len(cnt) >= 4 and cv.contourArea(cnt) > min_area and cv.isContourConvex(cnt):
                    cnt = cnt.reshape(-1, 2)
                    max_cos = np.max([angle_cos(cnt[i], cnt[(i+1) % 4], cnt[(i+2) % 4]) for i in xrange(4)])
                    if max_cos < max_skew:
                        squares.append(cnt)
    return squares


def main():
    from glob import glob
    for fn in glob("./*."+image_format):
        img = cv.imread(fn)
        squares = find_squares(img)
        # cv.drawContours(img, squares, 0, (0, 255, 0), 3)

        # show image
        # cv.imshow('squares', img)

        if squares:
            rect = cv.minAreaRect(squares[0])

            box = cv.boxPoints(rect)
            box = np.int0(box)

            # cv.drawContours(img, [box], 0, (0, 0, 255), 2)

            width = int(rect[1][0])
            height = int(rect[1][1])

            src_pts = box.astype("float32")
            # coordinate of the points in box points after the rectangle has been straightened
            dst_pts = np.array([[0, height - 1],
                                [0, 0],
                                [width - 1, 0],
                                [width - 1, height - 1]], dtype="float32")

            # the perspective transformation matrix
            M = cv.getPerspectiveTransform(src_pts, dst_pts)

            # directly warp the rotated rectangle to get the straightened rectangle
            warped = cv.warpPerspective(img, M, (width, height))

            # show image
            # cv.imshow("crop_img.jpg", warped)
            cv.imwrite(out_path+"/img"+str(time.time())+"."+image_format, warped)
            # cv.waitKey(0)

    print('Done')


if __name__ == '__main__':
    print(__doc__)
    os.mkdir(out_path)
    main()
    cv.destroyAllWindows()
