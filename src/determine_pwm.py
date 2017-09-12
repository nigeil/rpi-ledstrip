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
    gamma_lookup = [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
            0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  1,  1,  1,
            1,  1,  1,  1,  1,  1,  1,  1,  1,  2,  2,  2,  2,  2,  2,  2,
            2,  3,  3,  3,  3,  3,  3,  3,  4,  4,  4,  4,  4,  5,  5,  5,
            5,  6,  6,  6,  6,  7,  7,  7,  7,  8,  8,  8,  9,  9,  9, 10,
            10, 10, 11, 11, 11, 12, 12, 13, 13, 13, 14, 14, 15, 15, 16, 16,
            17, 17, 18, 18, 19, 19, 20, 20, 21, 21, 22, 22, 23, 24, 24, 25,
            25, 26, 27, 27, 28, 29, 29, 30, 31, 32, 32, 33, 34, 35, 35, 36,
            37, 38, 39, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 50,
            51, 52, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 66, 67, 68,
            69, 70, 72, 73, 74, 75, 77, 78, 79, 81, 82, 83, 85, 86, 87, 89,
            90, 92, 93, 95, 96, 98, 99,101,102,104,105,107,109,110,112,114,
            115,117,119,120,122,124,126,127,129,131,133,135,137,138,140,142,
            144,146,148,150,152,154,156,158,160,162,164,167,169,171,173,175,
            177,180,182,184,186,189,191,193,196,198,200,203,205,208,210,213,
            215,218,220,223,225,228,231,233,236,239,241,244,247,249,252,255 ]
    '''
    gamma = 2.1
    r_duty = int(r_duty * (r_duty/255.0) ** (gamma))
    g_duty = int(g_duty * (g_duty/255.0) ** (gamma))
    b_duty = int(b_duty * (b_duty/255.0) ** (gamma))
    '''

    
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


    r_duty = gamma_lookup[r_duty]
    g_duty = gamma_lookup[g_duty]
    b_duty = gamma_lookup[b_duty]

    ret = [r_duty,g_duty,b_duty]
    return ret
