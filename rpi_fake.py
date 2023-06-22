#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Methods to call light effect functions - but stubbed out so that all functions work on a macintosh
"""
import config
from includes import RGBW, Color

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
