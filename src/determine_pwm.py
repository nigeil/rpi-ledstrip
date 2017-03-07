#!/bin/python
# Convert hex color --> RGB color [0.0, 1.0] --> PWM duty cycle [0,255]
import matplotlib.colors as colors

def determine_pwm(hexColor):
    # Use matplotlib to convert to RGB
    r,g,b = colors.hex2color(hexColor)
    
    # Put into range [0,255] and change to int
    r_duty = int(r*255)
    g_duty = int(g*255)
    b_duty = int(b*255)

    # Perform gamma correction
    gamma = 2.1
    r_duty = int(r_duty * (r_duty/255.0) ** (gamma))
    g_duty = int(g_duty * (g_duty/255.0) ** (gamma))
    b_duty = int(b_duty * (b_duty/255.0) ** (gamma))
    
    # Force PWM duty cycle in range [0,255], in case something
    # malicious were to go on in the matplotlib conversion.
    if (r_duty > 255):
        r_duty = 255
    if (r_duty < 0):
        r_duty = 0
    if (g_duty > 255):
        g_duty = 255
    if (g_duty < 0):
        g_duty = 0
    if (b_duty > 255):
        b_duty = 255
    if (b_duty < 0):
        b_duty = 0
    

    ret = [r_duty,g_duty,b_duty]
    return ret
