# -*- coding:utf-8 -*-
""" 
@author:HuHongling

@file: morto.py 
@time: 2019/07/12
@contact: huhonglin@hwasmart.com
@site:  
@software: PyCharm 

"""
# from gpiozero import Robot, DigitalInputDevice
# from time import sleep
import os

"""
 Motor1E = 27
    Motor1A = 20
    R1 = 17
    17/26

    Motor2E = 16
    Motor2A = 21
    L1 = 26
"""
# SAMPLETIME = 1
#
#
# class Encoder(object):
#     def __init__(self, pin):
#         self._value = 0
#         encoder = DigitalInputDevice(pin)
#         encoder.when_activated = self._increment
#         encoder.when_deactivated = self._increment
#
#     def reset(self):
#         self._value = 0
#
#     def _increment(self):
#         self._value += 1
#
#     @property
#     def value(self):
#         return self._value
#
#
# r = Robot((27, 20), (16, 21)
#
# e1 = Encoder(17)
# e2 = Encoder(26)
#
# m1_speed = 1.0
# m2_speed = 1.0
#
# # r.value = (1.0, -1.0)
# r.left(0.0)
#
# while True:
#     print("e1 {} e2 {}".format(e1.value, e2.value)
#     sleep(SAMPLETIME)b
import pigpio
from time import sleep
import curses
pi = pigpio.pi()


class Motor:
    Motor1E = 27
    Motor1A = 20
    R1 = 17
    # 17/26

    Motor2E = 16
    Motor2A = 21
    L1 = 26
    HIGH = 1
    LOW = 0

    def __init__(self):
        os.system("sudo pigpiod")
        pi.set_mode(self.R1, pigpio.OUTPUT)
        pi.set_mode(self.L1, pigpio.OUTPUT)
        pi.set_mode(self.Motor1E, pigpio.OUTPUT)
        pi.set_mode(self.Motor1A, pigpio.OUTPUT)
        pi.set_mode(self.Motor2E, pigpio.OUTPUT)
        pi.set_mode(self.Motor2A, pigpio.OUTPUT)

    def backward(self):
        pi.write(self.Motor1E, self.HIGH)
        pi.write(self.Motor1A, self.LOW)
        pi.write(self.Motor2E, self.HIGH)
        pi.write(self.Motor2A, self.HIGH)

        sleep(2)

    def forward(self):
        pi.write(self.Motor1E, self.HIGH)
        pi.write(self.Motor1A, self.HIGH)
        pi.write(self.Motor2E, self.HIGH)
        pi.write(self.Motor2A, self.LOW)

        sleep(2)

    def left(self):
        pi.write(self.Motor1E, self.HIGH)
        pi.write(self.Motor1A, self.HIGH)
        pi.write(self.Motor2E, self.HIGH)
        pi.write(self.Motor2A, self.HIGH)

        sleep(2)

    def right(self):
        pi.write(self.Motor1E, self.HIGH)
        pi.write(self.Motor1A, self.LOW)
        pi.write(self.Motor2E, self.HIGH)
        pi.write(self.Motor2A, self.LOW)

        sleep(2)

    def stop(self):
        pi.write(self.Motor1E, self.LOW)
        pi.write(self.Motor2E, self.LOW)


    def get_signal(self):
        right_signal = pi.get_PWM_dutycycle(self.R1)
        left_signal = pi.get_PWM_dutycycle(self.L1)

        return right_signal, left_signal


motor = Motor()

screen = curses.initscr()
curses.noecho()
curses.cbreak()
screen.keypad(True)
try:
    while True:
        char = screen.getch()
        if char == ord('q'):
            break
        elif char == curses.KEY_UP:
            motor.forward()
        elif char == curses.KEY_DOWN:
            motor.backward()
        elif char == curses.KEY_RIGHT:
            motor.right()
        elif char == curses.KEY_LEFT:
            motor.left()
        elif char == 10:
            motor.stop()
finally:
    curses.nocbreak();
    screen.keypad(0)
    curses.echo()
    curses.endwin()
