#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Methods to call light effect functions

built upon: https://github.com/rpi-ws281x/rpi-ws281x-python/blob/master/examples/strandtest.py

"""
__author___ = "Jay Crossler"
__status__ = "Development"

import platform
import config

if platform.system() == 'Darwin':
    # Doesn't import on macs
    from rpi_fake import PixelStrip, Color
else:
    from rpi_ws281x import PixelStrip, Color
import time


LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

status = 'None'
stop_flag = False

# TODO: Remove texts
rainbow_text = "rainbow"
off = "all off"

def initialize_lighting():

    # Build Strip objects for multiple strands
    for i in config.setting('strands'):
        strip = config.setting('strands')[i]
        led_count = strip['size']
        pin = strip['pin']
        light_strip = PixelStrip(led_count, pin, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
        # Initialize the library (must be called once before other functions).
        light_strip.begin()
        config.light_strips.append(light_strip)


def get_status():
    global status
    if status is None:
        status = off
    return status


def set_status(state):
    global status
    status = state
    return


def func_color(r, g, b):
    global stop_flag
    stop_flag = True
    set_status("Wipe: {}, {}, {}".format(r,g,b))
    for light_strip in config.light_strips:
        color_wipe(light_strip, Color(r, g, b))
    return


def func_rainbow(light_strip):
    set_status(rainbow_text)
    run_rainbow(light_strip)
    return


def func_clear():
    global stop_flag
    stop_flag = True
    set_status(off)
    for light_strip in config.light_strips:
        clear(light_strip)
    return

def run_rainbow(light_strip):
    """Vary the colors in a rainbow pattern, slightly changing brightness, and
    quit if stop_flag set.

    NOTE: Stop flag might not be needed as the process should be killed automatically."""
    global stop_flag
    stop_flag = False

    b = 80
    while not stop_flag:
        try:
            light_strip.setBrightness(b)
            if not stop_flag:
                rainbow_cycle(light_strip)
                # theater_chase_rainbow(stripe)
                b -= 10
            if b <= 30:
                while b <= 80 and not stop_flag:
                    light_strip.setBrightness(b)
                    rainbow_cycle(light_strip)
                    # theater_chase_rainbow(stripe)
                    if not stop_flag:
                        b += 10
                b = 80

        except KeyboardInterrupt:
            config.log.warn("KeyboardInterrupt")
            exit()

        except Exception as e:
            config.log.error("Any error occurs: " + str(e))
            exit()

    config.log.info('rainbow run stopped')
    reset_strip(light_strip)
    return


# Define functions which animate LEDs in various ways.
def color_wipe(strip, color, wait_ms=10, start=0, stop=None):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        if wait_ms > 0:
            strip.show()
            time.sleep(wait_ms / 1000.0)
    if wait_ms == 0:
        strip.show()


def reset_strip(strip):
    color_wipe(strip, Color(0, 0, 0), wait_ms=0)
    return


def clear(strip):
    """Clear all pixels."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0,0,0))
    strip.show()


def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)


def rainbow_cycle(strip, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    global stop_flag

    for j in range(256 * iterations):
        if not stop_flag:
            for i in range(strip.numPixels()):
                if not stop_flag:
                    strip.setPixelColor(i, wheel(
                        (int(i * 256 / strip.numPixels()) + j) & 255))
            strip.show()
            time.sleep(wait_ms / 1000.0)

# Not Used:
def rainbow(strip, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256 * iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i + j) & 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)

def theater_chase(strip, color, wait_ms=50, iterations=10):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, color)
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, 0)

def theater_chase_rainbow(strip, wait_ms=50):
    """Rainbow movie theater light style chaser animation."""
    for j in range(256):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, wheel((i + j) % 255))
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, 0)


if __name__ == '__main__':
    pass