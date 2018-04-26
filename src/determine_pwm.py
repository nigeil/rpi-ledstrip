#!/bin/python
# Convert hex color --> RGB color [0.0, 1.0] --> PWM duty cycle [0,255]
import matplotlib.colors as colors
from cie1931 import cie1931

def determine_pwm(hexColor):
    # Use matplotlib to convert to RGB
    duty = colors.hex2color(hexColor)

    # Perform lightness correction
    duty = [cie1931(d) for d in duty]

    # Put into range [0,max_duty] and change to int
    max_duty = 2000
    duty = [int(d * max_duty) for d in duty]

    return duty
