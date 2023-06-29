import os, sys, time
import pigpio
import HiwonderSDK.ActionGroupControl as AGC

key1_pin = 13

if __name__ == "__main__":
    os.system('sudo pigpiod')
    
    time.sleep(1)
    pi = pigpio.pi()
    pi.set_mode(key1_pin, pigpio.INPUT)
    pi.set_pull_up_down(key1_pin, pigpio.PUD_UP)
    
    key1_pressed = False
  
    while True:
        if pi.read(key1_pin) == 0:
            time.sleep(0.05)
            if pi.read(key1_pin) == 0:
                if key1_pressed == False:
                    key1_pressed = True
                    print('start action')
                    AGC.runAction('clip')
            else:               
                key1_pressed = False
                continue 
            time.sleep(0.05)
            
        else:
            count = 0
            key1_pressed = False
            key2_pressed = False
            time.sleep(0.05)



