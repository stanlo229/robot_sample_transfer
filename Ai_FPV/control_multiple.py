import time
from ArmIK.ArmMoveIK import *
import Board

if __name__ == "__main__":
    AK = ArmIK()
    setBusServoPulse(1, 200, 500)
    time.sleep(1)
    setBusServoPulse(1, 700, 500)
    time.sleep(1)
    setBusServoPulse(1, 300, 500)
    time.sleep(1)

    setBusServoPulse(2, 200, 500)
    time.sleep(1)
    setBusServoPulse(2, 800, 500)
    time.sleep(1)
    setBusServoPulse(2, 500, 500)
    time.sleep(1)

    setBusServoPulse(3, 700, 500)
    time.sleep(1) 
    setBusServoPulse(3, 500, 500)
    time.sleep(1) 
    setBusServoPulse(3, 200, 500)
    time.sleep(1) 

    setBusServoPulse(4, 550, 500)
    time.sleep(1)
    setBusServoPulse(4, 800, 500)
    time.sleep(1)

    setBusServoPulse(5, 800, 500)
    time.sleep(1)
    setBusServoPulse(5, 500, 500)
    time.sleep(1)
    setBusServoPulse(5, 650, 500)
    time.sleep(1)

    setBusServoPulse(6, 200, 500)
    time.sleep(1)
    setBusServoPulse(6, 800, 1000)
    time.sleep(1)
    setBusServoPulse(6, 500, 500)
    time.sleep(1)

