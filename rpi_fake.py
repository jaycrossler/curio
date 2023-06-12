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
    def __init__(self, num, pin, freq_hz=800000, dma=10, invert=False,
            brightness=255, channel=0, strip_type=None, gamma=None):
                pass
    def __getitem__(self, pos):
        return [0,0,0]

    def __setitem__(self, pos, value):
        return [0,0,0]

    def __len__(self):
        return 0

    def _cleanup(self):
        pass

    def setGamma(self, gamma):
        pass

    def begin(self):
        pass

    def show(self):
        pass

    def setPixelColor(self, n, color):
        pass

    def setPixelColorRGB(self, n, red, green, blue, white=0):
        pass

    def getBrightness(self):
        return 0

    def setBrightness(self, brightness):
        pass

    def getPixels(self):
        return []

    def numPixels(self):
        """Return the number of pixels in the display."""
        return 0

    def getPixelColor(self, n):
        return [0,0,0]

    def getPixelColorRGB(self, n):
        return RGBW([0,0,0])

    def getPixelColorRGBW(self, n):
        return RGBW([0,0,0])


# Shim for back-compatibility
class Adafruit_NeoPixel(PixelStrip):
    pass