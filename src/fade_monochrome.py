#!/bin/python
# Returns a fade between the given intensity level and 1/3 its value

def fade_monochrome(intensity_start, intensity_end, subdivisions=150):
    ret = [i for i in range(intensity_start, intensity_end, -1)]

    ret_rev = list(reversed(ret))
    for i in range(0, len(ret_rev)):
        ret.append(ret_rev[i])

    return ret

if __name__ == "__main__":
    intensity_start = 100
    intensity_end = 25
    fade_list = fade_monochrome(intensity_start, intensity_end)
    for i in range(0, len(fade_list)):
        print("i = " + str(i) + " | color = " + str(fade_list[i]))
    print("First color == last color : " + str(fade_list[0] == fade_list[-1]))
