from threading import Timer

import os
import pigpio

PWM = 0


class PanTilt:
    """PanTilt HAT Driver
    Communicates with PanTilt HAT over i2c
    to control pan, tilt and light functions
    """

    def __init__(self,
                 idle_timeout=2,  # Idle timeout in seconds

                 servo1_min=575,
                 servo1_max=2325,
                 servo2_min=575,
                 servo2_max=2325
                 ):

        self._idle_timeout = idle_timeout
        os.system("sudo pigpiod")
        self.pi = pigpio.pi()
        self._servo_min = [servo1_min, servo2_min]
        self._servo_max = [servo1_max, servo2_max]

    def idle_timeout(self, value):
        """Set the idle timeout for the servos
        Configure the time, in seconds, after which the servos will be automatically disabled.
        :param value: Timeout in seconds
        """

        self._idle_timeout = value

    def _check_int_range(self, value, value_min, value_max):
        """Check the type and bounds check an expected int value."""

        if type(value) is not int:
            raise TypeError("Value should be an integer")
        if value < value_min or value > value_max:
            raise ValueError("Value {value} should be between {min} and {max}".format(
                value=value,
                min=value_min,
                max=value_max))

    def _check_range(self, value, value_min, value_max):
        """Check the type and bounds check an expected int value."""

        if value < value_min or value > value_max:
            raise ValueError("Value {value} should be between {min} and {max}".format(
                value=value,
                min=value_min,
                max=value_max))

    def _servo_us_to_degrees(self, us, us_min, us_max):
        """Converts pulse time in microseconds to degrees
        :param us: Pulse time in microseconds
        :param us_min: Minimum possible pulse time in microseconds
        :param us_max: Maximum possible pulse time in microseconds
        """

        self._check_range(us, us_min, us_max)
        servo_range = us_max - us_min
        angle = (float(us - us_min) / float(servo_range)) * 180.0
        return int(round(angle, 0))

    def _servo_degrees_to_us(self, angle, us_min, us_max):
        """Converts degrees into a servo pulse time in microseconds
        :param angle: Angle in degrees from -90 to 90
        """

        self._check_range(angle, 10, 160)
        #
        # angle += 90
        servo_range = us_max - us_min
        us = (servo_range / 180.0) * angle
        return us_min + int(us)

    def _servo_range(self, servo_index):
        """Get the min and max range values for a servo"""

        return (self._servo_min[servo_index], self._servo_max[servo_index])

    def servo_pulse_min(self, index, value):
        """Set the minimum high pulse for a servo in microseconds.
        :param value: Value in microseconds
        """

        if index not in [1, 2]:
            raise ValueError("Servo index must be 1 or 2")

        self._servo_min[index - 1] = value

    def servo_pulse_max(self, index, value):
        """Set the maximum high pulse for a servo in microseconds.
        :param value: Value in microseconds
        """

        if index not in [1, 2]:
            raise ValueError("Servo index must be 1 or 2")

        self._servo_max[index - 1] = value

    def servo_one(self, pan_pin, angle):
        """Set position of servo 1 in degrees.
        :param angle: Angle in degrees from -90 to 90
        """
        us_min, us_max = self._servo_range(0)
        us = self._servo_degrees_to_us(angle, us_min, us_max)
        self.pi.set_servo_pulsewidth(pan_pin, us)

    def servo_two(self, tilt_pin, angle):
        """Set position of servo 2 in degrees.
        :param angle: Angle in degrees from -90 to 90
        """

        us_min, us_max = self._servo_range(1)
        us = self._servo_degrees_to_us(angle, us_min, us_max)
        self.pi.set_servo_pulsewidth(tilt_pin, us)

    def _servo1_stop(self, pan_pin):
        self.pi.set_servo_pulsewidth(pan_pin, 0)

    def _servo2_stop(self, tilt_pin):
        self.pi.set_servo_pulsewidth(tilt_pin, 0)

    def servo_stop(self):
        self.pi.stop()

    pan = servo_one
    tilt = servo_two


if __name__ == '__main__':
    pth = PanTilt()
    pth.servo_one(23, 100)
    pth.servo_two(18, 105)
