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
import time
from colour import Color as colour_color
from itertools import chain
from math import sin, pi
from includes import blend_colors, clamp

animation_options = ['rainbow', 'wheel', 'pulsing', 'warp', 'blinkenlicht', 'blinking']

if platform.system() == 'Darwin':
    # This library doesn't import on Macintosh computers, ignore it and use a stub
    from rpi_fake import PixelStrip, Color
else:
    from rpi_ws281x import PixelStrip, Color


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


def valid_animation(anim):
    return anim in animation_options
# TODO: Lookup functions to run


def func_animation(animation_data):
    """Generic Animation controller, triggers correct animation based on options."""
    animation_config = animation_data.get('command_parsed', {})
    animation_command = animation_data.get('command', {})
    animation = animation_config.get('animation', None)

    global status
    status = animation

    light_strip = animation_data.get('strip')
    strand = animation_data.get('strand')

    if valid_animation(animation) and light_strip:
        id_list = animation_data.get('id_list', [])

        status = "Starting '{}' animation on strip {} with {} LEDs".format(animation_command, strand, len(id_list))
        config.log.info(status)

        # ['rainbow', 'wheel', 'pulsing', 'warp', 'blinkenlicht', 'blinking']
        if animation == 'rainbow':
            rainbow_cycle(light_strip, id_list=id_list)
        elif animation == 'pulsing':
            pulse_cycle(light_strip, anim_config=animation_config, id_list=id_list)

        else:
            # TODO: Add more
            pass

        # Should only run when an animation's cycle ends
        # TODO: Instead of clearing, should we set to light default?
        reset_strip(light_strip)

    return


def func_clear():
    global stop_flag
    stop_flag = True
    set_status("Clearing all lights")
    for light_strip in config.light_strips:
        clear(light_strip)
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


def rainbow_cycle(strip, wait_ms=20, id_list=None):
    """Draw rainbow that uniformly distributes itself across all pixels (or all pixels in id_list)."""

    pixels_to_loop_on = len(id_list) if id_list else strip.numPixels()

    for j in range(256):
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


# TODO: Pull speed out and use for wait_ms
def pulse_cycle(strip, wait_ms=20, anim_config=None, id_list=None):
    if anim_config is None:
        anim_config = {}

    """Pulse pixels repeatedly"""
    # TODO: Have a sin pattern where the center moves towards
    #  ending_color and back repeatedly

    starting_color = Color(0, 0, 1)
    ending_color = Color(1, 1, 1)
    provided_colors = anim_config.get('color_list', [])
    if len(provided_colors) > 1:
        ending_color = provided_colors[1]
    if len(provided_colors) > 0:
        starting_color = provided_colors[0]

    pulse_height = 100
    pulse_width = .5 # TODO: Have a way to change pulse width

    pixels_to_loop_on = len(id_list) if id_list else strip.numPixels()

    try:
        for height_of_pulse in chain(range(0, pulse_height), range(pulse_height, 0, -1)):
            for i in range(pixels_to_loop_on):
                pixel_to_set = id_list[i] if id_list else i

                # Note: .5*pi = 1, 1.5*pi = -1.  So sin(x + .5pi) + 1 ranges from 0to2 and 0to2pi
                # .5*(sin((2*pi*x) - (.5*pi))+1) goes from 0to1 and 0to1

                amplitude_of_point = .5*(sin((2*pi*i) - (.5*pi))+1)

                color = blend_colors(starting_color, ending_color, amplitude_of_point * height_of_pulse)
                strip.setPixelColor(pixel_to_set, color)
    except Exception as ex:
        print(ex)

    strip.show()
    time.sleep(wait_ms / 1000.0)


def find_ids(ids=None, id_start=None, id_end=None, limit_to=None):
    if ids and len(ids) > 0:
        id_list = ids.split(',')
    else:
        if id_start == 'NaN':
            id_start = None
        if id_end == 'NaN':
            id_end = None

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
            id_list = find_ids(ids, id_start, id_end, limit_to=strand.numPixels())

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
    animation = None
    loop_modifier = None
    loop_speed = None
    special = None
    color_list = []
    variation_list = []  # Color random variations that go with each color

    # If "off" passed in, field is set to: False, catch that with an if statement
    if text and len(text) > 3:
        # Format is 'color word(s)', 'animation', 'modifier', 'speed', 'special'
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

        # See if an animation or supporting information was entered
        if len(words) > 1:
            for word in words[1:]:
                text = word.strip().lower()
                if valid_animation(text):
                    animation = text
                if text in ['random', 'centered', 'cycled']:
                    loop_modifier = text
                if text in ['slow', '1', 1]:
                    loop_speed = 1
                if text in ['gentle', '2', 2]:
                    loop_speed = 2
                if text in ['medium', '3', 3]:
                    loop_speed = 3
                if text in ['speedy', '4', 4]:
                    loop_speed = 4
                if text in ['medium', '5', 5]:
                    loop_speed = 5
                if text in ['fast', '6', 6]:
                    loop_speed = 6

    return {'color_list': color_list, 'color_variations': variation_list, 'special': special,
            'animation': animation, 'loop_modifier': loop_modifier, 'loop_speed': loop_speed }


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
