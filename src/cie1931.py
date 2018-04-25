# from http://jared.geek.nz/2013/feb/linear-led-pwm, lightness correction for LEDS
# L ranges from [0, 100]
def cie1931(L):
    L = L*100.0
    if L <= 8:
        return (L/902.3)
    else:
        return ((L+16.0)/116.0)**3