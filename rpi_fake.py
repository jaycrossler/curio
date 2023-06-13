#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Methods to call light effect functions - but stubbed out so that all functions work on a mac
"""

class RGBW(int):
    def __new__(self, r, g=None, b=None, w=None):
        if (g, b, w) == (None, None, None):
            return int.__new__(self, r)
        else:
            if w is None:
                w = 0
            return int.__new__(self, (w << 24) | (r << 16) | (g << 8) | b)

    @property
    def r(self):
        return (self >> 16) & 0xff

    @property
    def g(self):
        return (self >> 8) & 0xff

    @property
    def b(self):
        return (self) & 0xff

    @property
    def w(self):
        return (self >> 24) & 0xff


def Color(red, green, blue, white=0):
    """Convert the provided red, green, blue color to a 24-bit color value.
    Each color component should be a value 0-255 where 0 is the lowest intensity
    and 255 is the highest intensity.
    """
    return RGBW(red, green, blue, white)


class PixelStrip:
    num = 0
    pin = 0
    brightness = 0
    leds = []

    def __init__(self, num, pin, freq_hz=800000, dma=10, invert=False,
            brightness=255, channel=0, strip_type=None, gamma=None):
        self.num = num
        self.pin = pin
        self.brightness = brightness
        self.leds = []
        for i in range(num):
            self.leds.append(Color(0,0,0))
        print("Added a string with leds: {}".format(self.leds))

    def __getitem__(self, pos):
        return self.leds[pos]

    def __setitem__(self, pos, value):
        self.leds[pos] = value
        return self.leds[pos]

    def __len__(self):
        return self.num

    def _cleanup(self):
        pass

    def setGamma(self, gamma):
        pass

    def begin(self):
        pass

    def show(self):
        pass

    def setPixelColor(self, n, color):
        self.leds[n] = color

    def setPixelColorRGB(self, n, red, green, blue, white=0):
        self.leds[n] = Color(red, green, blue)

    def getBrightness(self):
        return self.brightness

    def setBrightness(self, brightness):
        self.brightness = brightness

    def getPixels(self):
        return self.leds

    def numPixels(self):
        """Return the number of pixels in the display."""
        return self.num

    def getPixelColor(self, n):
        return self.leds[n]

    def getPixelColorRGB(self, n):
        return RGBW(self.leds[n])

    def getPixelColorRGBW(self, n):
        return RGBW(self.leds[n])


# Shim for back-compatibility
class Adafruit_NeoPixel(PixelStrip):
    pass