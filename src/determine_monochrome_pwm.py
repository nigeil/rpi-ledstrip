#!/bin/python
# convert intensity [0,100]% --> PWM [0,255]
from cie1931 import cie1931

def determine_monochrome_pwm(intensity):
# Use matplotlib to convert to [0,1] range
    duty = intensity / 100.0

    # Perform lightness correction
    duty = cie1931(duty)

    # Put into range [0,max_duty] and change to int
    max_duty = 2048
    duty = int(duty * max_duty)

    return duty

if __name__ == "__main__":
    x = range(0,101,5)
    y = [determine_monochrome_pwm(a) for a in x]
    for a,b in zip(x,y):
        print((a,b))
