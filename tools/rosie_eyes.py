# -*- coding: utf-8 -*-

# @Time    : 2019/4/3 17:08
# @Author  : HuHongLin
# @Project : hwasmart-robot
# @FileName: rosie_eyes.py
# @Software: PyCharm

import spidev
import time
from random import randint


class MatrixLED:

    # Register address map, specified in MAX7219 datasheet
    # https://datasheets.maximintegrated.com/en/ds/MAX7219-MAX7221.pdf

    MAX7219_REG_NOOP = 0x0
    MAX7219_REG_DIGIT0 = 0x1
    MAX7219_REG_DIGIT1 = 0x2
    MAX7219_REG_DIGIT2 = 0x3
    MAX7219_REG_DIGIT3 = 0x4
    MAX7219_REG_DIGIT4 = 0x5
    MAX7219_REG_DIGIT5 = 0x6
    MAX7219_REG_DIGIT6 = 0x7
    MAX7219_REG_DIGIT7 = 0x8
    MAX7219_REG_DECODEMODE = 0x9
    MAX7219_REG_INTENSITY = 0xA
    MAX7219_REG_SCANLIMIT = 0xB
    MAX7219_REG_SHUTDOWN = 0xC
    MAX7219_REG_DISPLAYTEST = 0xF

    def __init__(self, spi_port = 0, spi_device = 0, matrix_size = 8):
        self._spi = spidev.SpiDev()
        self._spi.open(spi_port, spi_device)
        self._spi.max_speed_hz = 1000000
        self._matrix_size = matrix_size
        self._send_byte(self.MAX7219_REG_SCANLIMIT, self._matrix_size - 1)
        self._send_byte(self.MAX7219_REG_DECODEMODE, 0)
        self._send_byte(self.MAX7219_REG_DISPLAYTEST, 0)
        self.intensity = 7
        self.set_intensity(self.intensity)
        self._send_byte(self.MAX7219_REG_SHUTDOWN, 1)

    def _send_byte(self, register = None, data = None):
        # Use SPI xfer method to send register, followed by data to MAX7219
        self._spi.xfer([register, data, register, data])

    def set_matrix(self, array):
        # Convert tuple of 1s and 0s into strings represting each line of the display
        # and dispatch each as bytes
        if len(array) == self._matrix_size:
            _count = 0
            # Rotate the array 90 degrees as both of our screens are at 90 degrees
            array = list(zip(*array[::-1]))
            while _count < self._matrix_size:
                _bits = "".join(map(str, array[_count]))
                if len(_bits) == self._matrix_size:
                    _byte = int(_bits, 2)
                    self._send_byte(_count + 1, _byte)
                    _count += 1
                else:
                   raise ValueError("Matrix size must be the expected size")
        else:
            raise ValueError("Matrix size must be the expected size")

    def set_intensity(self, intensity = 7):
        self._send_byte(self.MAX7219_REG_INTENSITY, intensity)
        self.intensity = intensity

    def clear(self):
        for _col in range(self._matrix_size):
            self._send_byte(_col + 1, 0)

class EyeController:

    # Tuples representing the matrix display

    EYES_HAPPY = ((0,0,0,0,0,0,0,0),
                  (0,0,0,1,1,0,0,0),
                  (0,0,1,0,0,1,0,0),
                  (0,1,0,0,0,0,1,0),
                  (0,1,0,1,1,0,1,0),
                  (0,1,1,0,0,1,1,0),
                  (0,1,0,0,0,0,1,0),
                  (0,0,0,0,0,0,0,0))

    EYES_SLEEPY = ((0,0,0,0,0,0,0,0),
                  (0,0,0,1,1,0,0,0),
                  (0,0,1,0,0,1,0,0),
                  (0,1,0,0,0,0,1,0),
                  (0,1,0,1,1,0,1,0),
                  (0,0,1,0,0,1,0,0),
                  (0,0,0,1,1,0,0,0),
                  (0,0,0,0,0,0,0,0))

    EYES_WATCH_L = ((0,0,0,1,1,0,0,0),
                  (0,0,1,0,0,1,0,0),
                  (0,1,0,0,0,0,1,0),
                  (0,1,1,1,0,0,1,0),
                  (0,1,1,1,0,0,1,0),
                  (0,1,0,0,0,0,1,0),
                  (0,0,1,0,0,1,0,0),
                  (0,0,0,1,1,0,0,0))

    EYES_WATCH_C = ((0,0,0,1,1,0,0,0),
                  (0,0,1,0,0,1,0,0),
                  (0,1,0,0,0,0,1,0),
                  (0,1,0,1,1,0,1,0),
                  (0,1,0,1,1,0,1,0),
                  (0,1,0,0,0,0,1,0),
                  (0,0,1,0,0,1,0,0),
                  (0,0,0,1,1,0,0,0))

    EYES_WATCH_R = ((0,0,0,1,1,0,0,0),
                  (0,0,1,0,0,1,0,0),
                  (0,1,0,0,0,0,1,0),
                  (0,1,0,0,1,1,1,0),
                  (0,1,0,0,1,1,1,0),
                  (0,1,0,0,0,0,1,0),
                  (0,0,1,0,0,1,0,0),
                  (0,0,0,1,1,0,0,0))

    EYES_BROKEN = ((0,0,0,0,0,0,0,0),
                  (0,1,0,0,0,0,1,0),
                  (0,0,1,0,0,1,0,0),
                  (0,0,0,1,1,0,0,0),
                  (0,0,0,1,1,0,0,0),
                  (0,0,1,0,0,1,0,0),
                  (0,1,0,0,0,0,1,0),
                  (0,0,0,0,0,0,0,0))

    def __init__(self):
        self.ml1 = MatrixLED()
        self.ml1.set_matrix(self.EYES_SLEEPY)

    def set_intensity(self, intensity):
        self.ml1.set_intensity(intensity)

    def set_happy(self):
        self.ml1.set_matrix(self.EYES_HAPPY)

    def set_sleepy(self):
        self.ml1.set_matrix(self.EYES_SLEEPY)

    def set_broken(self):
        self.ml1.set_matrix(self.EYES_BROKEN)

    def set_watch_centre(self):
        self.ml1.set_matrix(self.EYES_WATCH_C)

    def set_watch_left(self):
        self.ml1.set_matrix(self.EYES_WATCH_L)

    def set_watch_right(self):
        self.ml1.set_matrix(self.EYES_WATCH_R)

    def clear(self):
        self.ml1.clear()

if __name__ == "__main__":
    ec1 = EyeController()
    while True:
        time.sleep(randint(1,5))
        # Randomly choose one of the eyes available
        _option = randint(1,6)
        if _option == 1:
            ec1.set_happy()
        elif _option == 2:
            ec1.set_sleepy()
        elif _option == 3:
            # Couple of intermittent flashes for broken effect
            ec1.clear()
            time.sleep(0.2)
            ec1.set_broken()
            time.sleep(0.2)
            ec1.clear()
            time.sleep(0.2)
            ec1.set_broken()
        elif _option == 4:
            ec1.set_watch_centre()
        elif _option == 5:
            ec1.set_watch_left()
        elif _option == 6:
            ec1.set_watch_right()