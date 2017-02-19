#!/bin/python
# Returns a fade between two given colors

import matplotlib.colors as colors
import colorsys

def fade(hexColor0, hexColor1, subdivisions=50):
    # Convert to RGB [0.0, 1.0]
    rgbColor0 = colors.hex2color(hexColor0)    
    rgbColor1 = colors.hex2color(hexColor1)

    # Declare hex fade array
    ret = []
    
    # Calculate difference of hue between start/end colors (HSV coords)
    fadeColorStart = list(colorsys.rgb_to_hsv(*rgbColor0))
    fadeColorEnd   = list(colorsys.rgb_to_hsv(*rgbColor1))
    fadeColorDifference = abs(fadeColorStart[0] - fadeColorEnd[0])
    
    # Generate the fade in HSV space, appending HEX values to fade array
    for i in range(0, subdivisions + 1):
        fadeColor = list(fadeColorStart)
        fadeColor[0] += i * (fadeColorDifference/subdivisions)
        fadeColor = colorsys.hsv_to_rgb(*fadeColor)
        fadeColor = colors.rgb2hex(fadeColor)
        ret.append(fadeColor)

    ret_rev = list(reversed(ret))
    for i in range(0, len(ret_rev)):
        ret.append(ret_rev[i])

    return ret

if __name__ == "__main__":
    color0 = "#f4c842"
    color1 = "#c242f4"
    fade_list = fade(color0, color1)
    for i in range(0, len(fade_list)):
        print("i = " + str(i) + " | color = " + str(fade_list[i]))
