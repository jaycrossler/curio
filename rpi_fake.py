#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Methods to call light effect functions - but stubbed out so that all functions work on a macintosh
"""
import config


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
        return self & 0xff

    @property
    def w(self):
        return (self >> 24) & 0xff


def Color(red, green, blue, white=0):
    """Convert the provided red, green, blue color to a 24-bit color value.
    Each color component should be a value 0-255 where 0 is the lowest intensity
    and 255 is the highest intensity.
    """
    return RGBW(red, green, blue, white)

times_set = 0

class PixelStrip:
    num = 0
    pin = 0
    brightness = 0
    leds = []
    current_strip = None

    def __init__(self, num, pin, freq_hz=800000, dma=10, invert=False,
                 brightness=255, channel=0, strip_type=None, gamma=None):
        self.num = num
        self.pin = pin
        self.brightness = brightness
        self.leds = []
        for i in range(num):
            self.leds.append(Color(0, 0, 0))
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
        self.setColorInDB(n, color)

    def setPixelColorRGB(self, n, red, green, blue, white=0):
        color = Color(red, green, blue)
        self.leds[n] = color
        global times_set
        times_set += 1
        self.setColorInDB(n, color)

    def setColorInDB(self, n, color):
        global times_set
        times_set += 1
        if times_set % 100 == 0:
            for i in range(self.numPixels()):
                # Use CurrentStrip, or find the strip number if not set
                # TODO: Improve this way of looking up strip, maybe on init?
                if isinstance(self.current_strip, type(None)):
                    j = 0
                    for s in config.light_strips:
                        if s == self:
                            self.current_strip = j
                        j += 1

                config.set_color(self.current_strip, n, color)

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
