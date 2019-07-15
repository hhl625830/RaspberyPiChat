#-*- coding:utf-8 -*-  
""" 
@author:HuHongling

@file: servo_pigpio.py
@time: 2019/07/10
@contact: huhonglin@hwasmart.com
@site:  
@software: PyCharm 

"""
import pigpio
from time import sleep
pin = 23
# connect to the
pi = pigpio.pi()             # exit script if no connection
if not pi.connected:
   exit()

# loop forever
while True:

    pi.set_servo_pulsewidth(pin, 0)    # off
    sleep(1)
    pi.set_servo_pulsewidth(pin, 500) # position anti-clockwise
    sleep(1)
    pi.set_servo_pulsewidth(pin, 1500) # middle
    sleep(1)
    pi.set_servo_pulsewidth(pin, 2500) # position clockwise
    sleep(1)
