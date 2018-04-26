#!/bin/python
# implementation of required functions for rpi-gpio
# This 'library' is used iff running on a system that does not have the
# rpi-gpio libraries loaded - mostly for testing on my main system.

class pi():
    state = 'dummy'

    def set_PWM_dutycycle(self, pin_number, duty_cycle):
        return 0

    def set_PWM_range(self, pin_number, duty_cycle):
        return 0

    def set_servo(self, pin_number, duty_cycle):
    	return 0
    
    def __init__(self):
        self.state ='dummy_initialized'

class Servo():
	def set_PWM_dutycycle(self, pin_number, duty_cycle):
		return 0

	def set_servo(self, pin_number, duty_cycle):
		return 0

	def __init__(self):
		self.state ='dummy_initialized'


if __name__ == "__main__":
    my_pi = pi()
    print("my_pi.state == " + str(my_pi.state))
    my_pi.set_PWM_dutycycle(1, 1)
