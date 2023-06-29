#!/usr/bin/python3
# coding=utf8
import cv2
from pyzbar import pyzbar
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
import HiwonderSDK.Board as Board

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)
    
AK = ArmIK()
AK.setPitchRangeMoving((0, 10, 18), 0, -30, -90, 1500)


def run(image):
    # 找到图像中的条形码并解码每个条形码
    barcodes = pyzbar.decode(image)
    # 循环检测到的条形码
    for barcode in barcodes:
        # 提取条形码的边界框位置
        (x, y, w, h) = barcode.rect
        # 绘出图像上条形码的边框
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)

        barcodeData = barcode.data.decode("utf-8")
        barcodeType = barcode.type
        # 在图像上绘制条形码数据和条形码类型
        text = "{} ({})".format(barcodeData, barcodeType)
        cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    return image

if __name__ == '__main__':
    
    cap = cv2.VideoCapture(-1) #读取摄像头
    
    while True:
        ret, img = cap.read()
        if ret:
            frame = img.copy()
            Frame = run(frame)           
            cv2.imshow('Frame', Frame)
            key = cv2.waitKey(1)
            if key == 27:
                break
        else:
            time.sleep(0.01)
    cv2.destroyAllWindows()
