#!/usr/bin/python3
# coding=utf8
import sys
from cv2 import cv2
import numpy
import time

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

if __name__ == '__main__':
    time.sleep(1)
    cap = cv2.VideoCapture(1) #读取摄像头
    while True:
        ret, img = cap.read()
        if ret:
            frame = img.copy()
            cv2.imshow('frame', frame)
            key = cv2.waitKey(1)
            if key == 27:
                break
        else:
            time.sleep(0.01)
    cv2.destroyAllWindows()
