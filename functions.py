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
from colour import Color as colour_color

if platform.system() == 'Darwin':
    # This library doesn't import on Macintosh computers, ignore it and use a stub
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
        config.log.info("Added light strip {} on pin {} size {}".format(i, pin, led_count))
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
    set_status("Wipe: {}, {}, {}".format(r, g, b))
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
    quit if stop_flag set."""
    global stop_flag
    stop_flag = False

    config.log.info("Starting rainbow animation on strip with {} leds".format(light_strip.numPixels()))

    rainbow_cycle(light_strip)

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
        strip.setPixelColor(i, Color(0, 0, 0))
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
        if stop_flag:
            break
        for i in range(strip.numPixels()):
            if stop_flag:
                break
            try:
                strip.setPixelColor(i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))
            except IndexError:
                config.log.warn("IndexError using {} when numPixels is {} and"
                                " length of leds is {}".format(i, strip.numPixels(), len(strip.leds)))

            strip.show()
            time.sleep(wait_ms / 1000.0)


def setup_lights_from_configuration(strands_config):
    # Expects that light strips have been configured, then sets starting colors and animations
    strand_id = 0
    for strand_name in strands_config:
        strand = config.light_strips[strand_id]
        data = strands_config[strand_name]
        ids_data = data['ids'] if 'ids' in data else []
        id_ranges_data = data['id_ranges'] if 'id_ranges' in data else []

        for id_range_data_name in id_ranges_data:
            id_range_data = id_ranges_data[id_range_data_name]
            ids = id_range_data['ids'] if 'ids' in id_range_data else ""
            id_start = id_range_data['id_start'] if 'id_start' in id_range_data else ""
            id_end = id_range_data['id_end'] if 'id_end' in id_range_data else ""
            animations = id_range_data['animations'] if 'animations' in id_range_data else []
            default_anim = animations['default'] if 'default' in animations else 'off'
            parsed_anim = parse_animation_text(default_anim)
            default_color = parsed_anim['color']

            if len(ids) > 0:
                id_list = ids.split(',')
            else:
                if 'id_start' in id_range_data and 'id_end' in id_range_data:
                    id_list = range(int(id_start), int(id_end))
                else:
                    id_list = []

            for pin in id_list:
                led = int(pin)
                if led < strand.numPixels():
                    strand.setPixelColor(led, default_color)
                else:
                    config.log.warning('Tried to set LED from invalid config entry: strand {} {}'.format(id_range_data_name, led))

        for id_data_led in ids_data:
            id_data = ids_data[id_data_led]
            animations = id_data['animations'] if 'animations' in id_data else []
            default_anim = animations['default'] if 'default' in animations else 'off'
            parsed_anim = parse_animation_text(default_anim)
            default_color = parsed_anim['color']
            strand.setPixelColor(int(id_data_led), default_color)

        strand_id += 1


def parse_animation_text(text):
    # If "off" passed in, field is set to: False, catch that
    loop = None
    loop_modifier = None
    loop_speed = None
    special = None

    if text and len(text) > 3:
        text = text.lower()

        words = text.split(" ")
        color_name = words[0]

        colour_rgb = colour_color(color_name)
        color = Color(int(colour_rgb.red * 255), int(colour_rgb.green * 255), int(colour_rgb.blue * 255))

        if 'puls' in text:
            loop = 'pulse'
        elif 'blink' in text:
            loop = 'blink'
        elif 'cycle' in text:
            loop = 'cycle'
        elif 'warp' in text:
            loop = 'warp'

        if 'rainbow' in text:
            special = 'rainbow'

        if 'random' in text:
            loop_modifier = 'random'

        if 'slow' in text:
            loop_speed = 4
        elif 'fast' in text:
            loop_speed = 2
        elif 'gentle' in text:
            loop_speed = 6

    else:
        color = 0

    return {'color': color, 'loop': loop, 'loop_modifier': loop_modifier, 'loop_speed': loop_speed, 'special': special}


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
