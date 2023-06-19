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
import random
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
        status = "Lights are off"
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


def func_rainbow(light_strip_data):
    set_status("Rainbow")
    run_rainbow(light_strip_data.get('strip'), light_strip_data.get('id_list'))
    return


def func_clear():
    global stop_flag
    stop_flag = True
    set_status("Clearing all lights")
    for light_strip in config.light_strips:
        clear(light_strip)
    return


def run_rainbow(light_strip, id_list=None):
    """Vary the colors in a rainbow pattern, slightly changing brightness, and
    quit if stop_flag set."""
    if id_list is None:
        id_list = []

    global stop_flag
    stop_flag = False

    config.log.info("Starting rainbow animation on strip with {} leds".format(light_strip.numPixels()))

    rainbow_cycle(light_strip, id_list=id_list)

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


def rainbow_cycle(strip, wait_ms=20, iterations=5, id_list=None):
    """Draw rainbow that uniformly distributes itself across all pixels (or all pixels in id_list)."""
    # TODO: Remove iterations variable

    global stop_flag

    pixels_to_loop_on = len(id_list) if id_list else strip.numPixels()

    for j in range(256 * iterations):
        if stop_flag:
            break
        for i in range(pixels_to_loop_on):
            if stop_flag:
                break
            try:
                pixel_to_set = id_list[i] if id_list else i
                strip.setPixelColor(pixel_to_set, wheel((int(i * 256 / pixels_to_loop_on) + j) & 255))
            except IndexError:
                config.log.warn("IndexError using {} when numPixels is {} and"
                                " length of leds is {}".format(i, strip.numPixels(), len(strip.leds)))

            strip.show()
            time.sleep(wait_ms / 1000.0)


def find_ids(ids=None, id_start=None, id_end=None, limit_to=None):
    if ids and len(ids) > 0:
        id_list = ids.split(',')
    else:
        if type(id_start) is str and len(id_start):
            id_start = int(id_start)
        if type(id_end) is str and len(id_end):
            id_end = int(id_end)

        if type(id_start) is int and type(id_end) is int:
            id_list = range(id_start, id_end)
        else:
            id_list = []

    id_list = [int(i) for i in id_list]

    if limit_to:
        for id_num in id_list:
            if int(id_num) > limit_to:
                id_list.remove(id_num)

    return id_list


def setup_lights_from_configuration(strands_config=None, set_lights_on=True):
    # Expects that light strips have been configured, then sets starting colors and animations
    if not strands_config:
        strands_config = config.settings.get('strands')
    light_data = []
    light_color_data = []
    mode_list = []
    
    strand_id = 0
    for strand_name in strands_config:
        config.log.info("Setting up default lights for strand - {}".format(strand_name))
        strand = config.light_strips[strand_id]
        data = strands_config.get(strand_name)
        ids_data = data.get('ids', [])
        id_ranges_data = data.get('id_ranges', [])

        led_database = []
        led_list = []
        for i in range(strand.numPixels()):
            led_database.append({})
            led_list.append(0)

        for id_range_data_name in id_ranges_data:
            id_range_data = id_ranges_data.get(id_range_data_name)

            ids = id_range_data.get('ids', "")
            id_start = id_range_data.get('id_start', "")
            id_end = id_range_data.get('id_end', "")
            id_list = find_ids(ids, id_start, id_end)

            animations = id_range_data.get('animations', [])
            default_anim = animations.get(config.current_mode, 'off')
            parsed_anim = parse_animation_text(default_anim)

            for anim in animations:
                if anim not in mode_list: mode_list.append(anim)

            for led_num in id_list:
                led = int(led_num)
                if led < strand.numPixels():
                    picked_color = color_from_list_with_range(parsed_anim)
                    if set_lights_on:
                        strand.setPixelColor(led, picked_color)
                    led_database[led] = {
                        'id': led, 'color': picked_color, 'name': id_range_data_name, 'anim_text': default_anim
                    }
                    led_list[led] = picked_color
                    # config.log.info("- Strand {} - Pixel {} - color: {}".format(strand_name, led, default_color))
                else:
                    config.log.warning('Invalid led animation config: strand {} {}'.format(id_range_data_name, led))

        for id_data_led in ids_data:
            id_data = ids_data[id_data_led]
            animations = id_data['animations'] if 'animations' in id_data else []
            default_anim = animations[config.current_mode] if config.current_mode in animations else 'off'
            id_name = id_data['name'] if 'name' in id_data else ''
            parsed_anim = parse_animation_text(default_anim)

            picked_color = color_from_list_with_range(parsed_anim)
            if set_lights_on:
                strand.setPixelColor(int(id_data_led), picked_color)
            led_database[id_data_led] = {
                'id': id_data_led, 'color': picked_color, 'name': id_name, 'anim_text': default_anim
            }
            led_list[id_data_led] = picked_color

            for anim in animations:
                if anim not in mode_list: mode_list.append(anim)

        # config.log.info("- Strand {} - Pixels: {} - color: {}".format(strand_name, ids_data, default_color))
        strand_id += 1
        if set_lights_on:
            strand.show()
        light_data.append(led_database)
        light_color_data.append(led_list)

        config.animation_modes = mode_list
    return light_data, light_color_data


def parse_animation_text(text):
    loop = None
    loop_modifier = None
    loop_speed = None
    special = None
    color_list = []
    variation_list = []  # Color random variations that go with each color

    # If "off" passed in, field is set to: False, catch that with an if statement
    if text and len(text) > 3:
        # Format is 'color word(s)', 'loop', 'modifier', 'speed', 'special'
        # example: "yellow, pulsing, random" or "red and white, pulsing" or "blue:.1"
        text = text.strip().lower()

        # Break by commas into named chunks
        words = text.split(",")
        color_name = words[0]

        # separate out multiple colors
        colors_names = color_name.split(' and ')
        for color_name_split in colors_names:
            try:
                # parse out any : after color names for random variations, eg Blue:.1 or Pink:.2:0:.1
                color_var_split = color_name_split.split(':')
                variations = []
                if len(color_var_split) > 1:
                    variations = color_var_split[1:]

                colour_rgb = colour_color(color_var_split[0])
                color = Color(int(colour_rgb.red * 255), int(colour_rgb.green * 255), int(colour_rgb.blue * 255))
                color_list.append(color)
                variation_list.append(variations)
            except:
                config.log.warning(
                    'Color "{}" not recognized from config.yaml strand animation settings'.format(color_name_split))

        # See if an animation was entered
        if len(words) > 1:
            for word in words[1:]:
                text = word.strip().lower()
                if text in ['pulse', 'blink', 'cycle', 'warp']:
                    loop = text
                if text in ['rainbow']:
                    special = text
                if text in ['random', 'console']:
                    loop_modifier = text
                if text in ['slow', 'fast', 'gentle', '1', '2', '3', '4', '5', '6']:
                    loop_speed = text

    return {'color_list': color_list, 'color_variations': variation_list, 'special': special,
            'loop': loop, 'loop_modifier': loop_modifier, 'loop_speed': loop_speed }


def color_from_list_with_range(parsed_animation):
    color_list = parsed_animation['color_list']
    modifier_list = parsed_animation['color_variations']

    if len(color_list):
        color_number_to_use = random.choice(range(len(color_list)))
        out_color = color_list[color_number_to_use]
        out_modifier = modifier_list[color_number_to_use] if len(modifier_list) >= color_number_to_use else []

        if len(out_modifier) > 0:
            out_color = random_color_range(out_color, out_modifier)
    else:
        out_color = 0

    return out_color


def random_color_range(color, ranges):
    # Start with a Color, then return another color close to it based on percentages in 'ranges'.
    # example: "Color(120, 100, 100), [.1]" or "Color(120, 100, 100), [.2,0,.2]"
    ranges = ranges or []
    range_r = range_g = range_b = 0
    if len(ranges) > 2:
        range_b = ranges[2]
    if len(ranges) > 1:
        range_g = ranges[1]
    if len(ranges) > 0:
        range_r = ranges[0]
    if len(ranges) == 1:
        range_g = range_r
        range_b = range_r

    range_r = int(float(range_r) * 255)
    range_g = int(float(range_g) * 255)
    range_b = int(float(range_b) * 255)

    r = color.r
    g = color.g
    b = color.b

    new_r = clamp(random.randint(r - range_r, r + range_r), 0, 255)
    new_g = clamp(random.randint(g - range_g, g + range_g), 0, 255)
    new_b = clamp(random.randint(b - range_b, b + range_b), 0, 255)

    return Color(new_r, new_g, new_b)


def clamp(val, minval, maxval):
    if val < minval: return minval
    if val > maxval: return maxval
    return val

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
