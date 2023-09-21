import time
from ArmIK.ArmMoveIK import *

if __name__ == "__main__":
    AK = ArmIK()
    # Bowing and Nodding
##    AK.setPitchRangeMoving((0, 15, 25), -45, -90, 0, 500)
##    time.sleep(0.5)
##    AK.setPitchRangeMoving((0, 15, 15), -45, -90, 0, 500)
##    time.sleep(0.5)
##    AK.setPitchRangeMoving((0, 15, 25), -45, -90, 0, 500)
##    time.sleep(0.5)
##    AK.setPitchRangeMoving((0, 15, 15), -45, -90, 0, 500)
##    time.sleep(0.5)
##    AK.setPitchRangeMoving((0, 15, 25), -45, -90, 0, 500)
##    time.sleep(0.5)
##    AK.setPitchRangeMoving((0, 15, 15), -45, -90, 0, 500)
##    time.sleep(0.5)
##    
##    # Shake head
##    AK.setPitchRangeMoving((5, 15, 25), -45, -90, 0, 300)
##    time.sleep(0.5)
##    AK.setPitchRangeMoving((-5, 15, 25), -45, -90, 0, 300)
##    time.sleep(0.5)
##    AK.setPitchRangeMoving((5, 15, 25), -45, -90, 0, 300)
##    time.sleep(0.5)
##    AK.setPitchRangeMoving((-5, 15, 25), -45, -90, 0, 300)
##    time.sleep(0.5)
##    AK.setPitchRangeMoving((5, 15, 25), -45, -90, 0, 300)
##    time.sleep(0.5)
##    AK.setPitchRangeMoving((-5, 15, 25), -45, -90, 0, 300)
##    time.sleep(0.5)
    AK.setPitchRangeMoving((0, 10, 7), -45, -90, 90, 1000)
    time.sleep(1)

