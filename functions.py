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
import time
from itertools import chain
from math import sin, pi
from includes import *


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

        if animation == 'rainbow':
            rainbow_cycle(light_strip, anim_config=animation_config, id_list=id_list)
        elif animation == 'warp':
            warp_cycle(light_strip, anim_config=animation_config, id_list=id_list)
        elif animation == 'pulsing':
            pulse_cycle(light_strip, anim_config=animation_config, id_list=id_list)
        elif animation == 'blinking':
            blink_cycle(light_strip, anim_config=animation_config, id_list=id_list)
        elif animation == 'blinkenlicht':
            blinkenlicht_cycle(light_strip, anim_config=animation_config, id_list=id_list)
        elif animation == 'twinkle':
            twinkle_cycle(light_strip, anim_config=animation_config, id_list=id_list)

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
def color_wipe(strip, color, wait_ms=10):
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


def rainbow_cycle(strip, anim_config=None, id_list=None):
    """Draw rainbow that uniformly distributes itself across all pixels (or all pixels in id_list)."""

    speed = anim_config.get('loop_speed', 3)
    wait_ms = remap(1, 6, .04, .001, speed)

    pixels_to_loop_on = len(id_list) if id_list else strip.numPixels()

    config.log.info("PULSE SPEED {} MS DELAY.  {} pixels".format(wait_ms, pixels_to_loop_on))

    while True:
        for j in range(256):
            for i in range(pixels_to_loop_on):
                try:
                    pixel_to_set = id_list[i] if id_list else i
                    color = wheel((int(i * 256 / pixels_to_loop_on) + j) & 255)
                    strip.setPixelColor(pixel_to_set, color)
                except IndexError:
                    config.log.warn("IndexError using {} when numPixels is {} and"
                                    " length of leds is {}".format(i, strip.numPixels(), len(strip.leds)))

            strip.show()
            time.sleep(wait_ms)


def twinkle_cycle(strip, anim_config=None, id_list=None):
    """twinkle/blink pixels repeatedly through each color in list """

    if anim_config is None:
        anim_config = {}

    # Get colors, and add yellow if no colors given
    provided_colors = anim_config.get('color_list', [])
    color_variations = anim_config.get('color_variations', [])
    if len(provided_colors) < 1:
        provided_colors.append(Color(200, 200, 0))
    if len(provided_colors) < 2:
        provided_colors.append(Color(247, 218, 76))

    speed = anim_config.get('loop_speed', 3)
    wait_ms = remap(1, 6, 100, 5, speed)  # Map speed setting from 1-6

    max_animation_amount = 2 + (5 * speed)  # Should be greater than 2 at least
    chance_to_increase_brightness = .05
    chance_to_change_colors = .05
    chance_to_start_a_twinkle = float(anim_config.get('density', .3))
    speed_to_blend = .05
    twinkle_variance = .2

    # Either loop on all pixels or the range passed in
    pixels_to_loop_on = len(id_list) if id_list else strip.numPixels()

    # Have a list for each pixel to show what percentage it's animated and color
    led_status_list = []
    led_color_list = []
    for i in range(pixels_to_loop_on):
        led_status_list.append(0)
        starting_color = random_color_with_range_from_list(provided_colors, color_variations, twinkle_variance)

        led_color_list.append(starting_color)
        # set all pixels to starting color

        pixel_to_set = id_list[i] if id_list else i
        strip.setPixelColor(pixel_to_set, starting_color)

    iteration = 0
    while True:
        # Loop through each pixel and randomly blend it towards a target color
        for i in range(pixels_to_loop_on):
            current_color = "unset"
            current_color_target = "unset"
            try:
                pixel_to_set = id_list[i] if id_list else i
                current_color = strip.getPixelColorRGB(pixel_to_set)
                current_color_target = led_color_list[i]
                current_animation_amount = led_status_list[i]

                if current_animation_amount >= max_animation_amount:  # It passed the goal, start de-animating it
                    # Make it negative to show that it should decrease
                    led_status_list[i] *= -1
                    current_color = blend_colors(current_color, current_color_target, speed_to_blend)
                elif (2 + speed/2) < current_animation_amount < max_animation_amount:  # It's animating toward target
                    current_color = blend_colors(current_color, current_color_target, speed_to_blend)
                    # Usually increase the brightness towards the target, but sometimes don't
                    if random.random() < chance_to_increase_brightness:
                        led_status_list[i] /= 2
                    else:
                        led_status_list[i] += random.random()

                    if random.random() < chance_to_change_colors:
                        led_color_list[i] = random_color_with_range_from_list(provided_colors, color_variations, twinkle_variance)

                elif 0 < current_animation_amount:  # It started animating, don't mess with it
                    led_status_list[i] += random.random()
                    current_color = blend_colors(current_color, current_color_target, speed_to_blend)
                elif current_animation_amount == 0:  # It is not animating
                    # Set it towards the target
                    if random.random() < (chance_to_start_a_twinkle * chance_to_start_a_twinkle):
                        led_status_list[i] += random.random()
                        new_color = random_color_range(current_color, twinkle_variance)
                        led_color_list[i] = new_color
                        current_color = Color(255, 255, 255)
                elif current_animation_amount > (-1 - speed/2):  # It's close enough to 0, end the animation
                    led_status_list[i] = 0
                    current_color = current_color_target
                else:  # It's negative, so should approach back to 0
                    led_status_list[i] += random.random()
                    current_color = blend_colors(current_color, current_color_target, speed_to_blend)

                strip.setPixelColor(pixel_to_set, current_color)

            # msg = "State [{}]: ".format(starting_color)
            # for i in range(len(led_status_list)):
            #     msg += "{:.2f},".format(led_status_list[i])
            # config.log.info(msg)

            except AttributeError as e:
                config.log.warn("Color error: current:{} target:{}. {}".format(current_color, current_color_target, e))

        iteration += 1
        strip.show()
        time.sleep(wait_ms / 1000.0)


def blinkenlicht_cycle(strip, anim_config=None, id_list=None):
    """Blink pixels through each color in list in a slow on/off style"""

    if anim_config is None:
        anim_config = {}

    # Get colors, and add yellow if no colors given
    provided_colors = anim_config.get('color_list', [])
    color_variations = anim_config.get('color_variations', [])
    if len(provided_colors) < 1:
        provided_colors.append(Color(0, 0, 0))
    if len(provided_colors) < 2:
        provided_colors.append(Color(247, 218, 76))

    speed = anim_config.get('loop_speed', 3)
    wait_ms = remap(1, 6, 100, 10, speed)  # Map speed setting from 1-6

    mode = anim_config.get('mode', 'linear')

    # TODO: Decide if these should be variables
    max_animation_amount = 2 + (5 * speed)  # Should be greater than 2 at least
    chance_to_increase_brightness = .05
    chance_to_change_colors = .05
    chance_to_start_a_twinkle = float(anim_config.get('density', .3))
    speed_to_blend = .05
    starting_color = provided_colors[0]

    # Either loop on all pixels or the range passed in
    pixels_to_loop_on = len(id_list) if id_list else strip.numPixels()

    # Have a list for each pixel to show what percentage it's animated and color
    led_status_list = []
    led_color_list = []
    for i in range(pixels_to_loop_on):
        led_status_list.append(0)
        led_color_list.append(starting_color)
        # set all pixels to starting color
        pixel_to_set = id_list[i] if id_list else i
        strip.setPixelColor(pixel_to_set, starting_color)

    iteration = 0
    while True:
        # Loop through each pixel and randomly blend it towards a target color
        new_color = random_color_with_range_from_list(provided_colors, color_variations, default_variation=.2)
        current_color = "unset"

        # A "state machine" represented by a float for each light, with lights changing behavior based on number
        try:
            for i in range(pixels_to_loop_on):
                pixel_to_set = id_list[i] if id_list else i
                current_animation_amount = led_status_list[i]
                current_color_target = led_color_list[i]
                current_color = strip.getPixelColorRGB(pixel_to_set)

                if current_animation_amount >= max_animation_amount:  # It passed the goal, start de-animating it
                    # Make it negative to show that it should decrease
                    led_status_list[i] *= -1
                    current_color = blend_colors(current_color, current_color_target, speed_to_blend)
                elif (2 + speed) < current_animation_amount < max_animation_amount:  # It's animating toward target
                    if mode == 'linear':
                        led_status_list[i] += random.random()
                        current_color = blend_colors(current_color, current_color_target, speed_to_blend)
                    else:
                        current_color = blend_colors(current_color, current_color_target, speed_to_blend)
                        # Usually increase the brightness towards the target, but sometimes don't
                        if random.random() < chance_to_increase_brightness:
                            led_status_list[i] /= 2
                        else:
                            led_status_list[i] += random.random()

                        if random.random() < chance_to_change_colors:
                            led_color_list[i] = new_color
                elif 0 < current_animation_amount:  # It started animating, don't mess with it
                    led_status_list[i] += random.random()
                    current_color = blend_colors(current_color, current_color_target, speed_to_blend)
                elif current_animation_amount == 0:  # It is not animating
                    # Set it towards the target
                    if random.random() < (chance_to_start_a_twinkle * chance_to_start_a_twinkle):
                        led_status_list[i] += random.random()
                        led_color_list[i] = new_color
                        current_color = blend_colors(current_color, new_color, speed_to_blend)
                elif current_animation_amount > (-1 - speed):  # It's close enough to 0, end the animation
                    led_status_list[i] = 0
                    led_color_list[i] = starting_color
                    current_color = starting_color
                else:  # It's negative, so should approach back to 0
                    led_status_list[i] += random.random()
                    current_color = blend_colors(current_color, starting_color, speed_to_blend)

                strip.setPixelColor(pixel_to_set, current_color)
            
            # msg = "State [{}]: ".format(starting_color)
            # for i in range(len(led_status_list)):
            #     msg += "{:.2f},".format(led_status_list[i])
            # config.log.info(msg)

        except AttributeError as e:
            config.log.warn("Color error:{} - {} - {}. {}".format(current_color, starting_color, new_color, e))

        iteration += 1
        strip.show()
        time.sleep(wait_ms / 1000.0)


def blink_cycle(strip, anim_config=None, id_list=None):
    """blink pixels repeatedly through each color in list """

    if anim_config is None:
        anim_config = {}

    # Get colors, and add white and black if none listed
    provided_colors = anim_config.get('color_list', [])
    if len(provided_colors) < 1:
        provided_colors.append(Color(255, 255, 255))
    if len(provided_colors) < 2:
        provided_colors.append(Color(0, 0, 0))

    speed = anim_config.get('loop_speed', 3)
    wait_ms = remap(1, 6, 2000, 100, speed)  # Map speed setting from 1-6

    # Either loop on all pixels or the range passed in
    pixels_to_loop_on = len(id_list) if id_list else strip.numPixels()

    iteration = 0
    while True:
        current_color = provided_colors[iteration % len(provided_colors)]

        for i in range(pixels_to_loop_on):
            pixel_to_set = id_list[i] if id_list else i
            strip.setPixelColor(pixel_to_set, current_color)
        iteration += 1
        strip.show()
        time.sleep(wait_ms / 1000.0)


def warp_cycle(strip, anim_config=None, id_list=None):
    """Pulse pixels repeatedly in a sine wave pattern where the center moves towards
     ending_color and back repeatedly """

    if anim_config is None:
        anim_config = {}

    # Use first two colors passed in or go from blue to white
    starting_color = Color(0, 0, 255)
    ending_color = Color(255, 255, 255)
    provided_colors = anim_config.get('color_list', [])
    if len(provided_colors) > 1:
        ending_color = provided_colors[1]
    if len(provided_colors) > 0:
        starting_color = provided_colors[0]

    speed = anim_config.get('loop_speed', 3)
    wait_ms = remap(1, 6, 80, 2, speed)  # Map speed setting from 1-6 into 2-80ms delay

    pulse_height = 100
    # TODO: Have a way to change pulse width
    # TODO: Add random color fluctuations, have multiple light set 'shapes'

    # Either loop on all pixels or the range passed in
    pixels_to_loop_on = len(id_list) if id_list else strip.numPixels()

    while True:
        # iteration = 0
        for height_of_pulse in chain(range(0, pulse_height), range(pulse_height, 0, -1)):
            # pix = []
            for i in range(pixels_to_loop_on):
                pixel_to_set = id_list[i] if id_list else i

                # Note on math: .5*pi = 1, 1.5*pi = -1.  So sin(x + .5pi) + 1 ranges from 0to2 and 0to2pi
                # .5*(sin((2*pi*x) - (.5*pi))+1) goes from 0to1 and 0to1
                x_range = (i+.5)/(pixels_to_loop_on+1)  # Set it so the first is always a little into the color mix
                amplitude_of_point = .5*(sin((2*pi*x_range) - (.5*pi))+1)
                y_range = height_of_pulse/pulse_height

                color = blend_colors(starting_color, ending_color, amplitude_of_point * y_range)
                strip.setPixelColor(pixel_to_set, color)
                # pix.append(color_str(color))
            strip.show()
            # config.log.info("{}: [{} {}] {}".format(
            #   iteration, color_str(starting_color), color_str(ending_color), " ".join(pix)))
            # iteration += 1
            time.sleep(wait_ms / 1000.0)


def pulse_cycle(strip, anim_config=None, id_list=None):
    """Pulse pixels repeatedly in a sine wave pattern where the center moves towards
     ending_color and back repeatedly """

    if anim_config is None:
        anim_config = {}

    # Use first two colors passed in or go from blue to white
    starting_color = Color(0, 0, 0)
    ending_color = Color(255, 255, 255)
    provided_colors = anim_config.get('color_list', [])
    if len(provided_colors) > 1:
        ending_color = provided_colors[1]
    if len(provided_colors) > 0:
        starting_color = provided_colors[0]

    speed = anim_config.get('loop_speed', 3)
    mode = anim_config.get('mode', 'linear')
    wait_ms = remap(1, 6, 200, 50, speed)  # Map speed setting from 1-6 into expected delay
    pulse_height = 100

    # Either loop on all pixels or the range passed in
    pixels_to_loop_on = len(id_list) if id_list else strip.numPixels()

    while True:
        # Go from 0 to pulse_height back down to 0
        for height_of_pulse in chain(range(0, pulse_height), range(pulse_height, 0, -1)):

            height = height_of_pulse / pulse_height
            if mode == 'sin':
                height = .5 * (1 + sin((1.5 + height) * pi))
            elif mode == 'spike':
                regular_sin = .5 * (1 + sin((2 * pi * height) + (1.5 * pi)))  # maps to 0..1/0..1
                height = 2 - (regular_sin**-2)  # make it thinner and spikey, then only take if positive
                if height < 0:
                    height = 0
            elif mode == 'linear':
                pass  # use base height

            color = blend_colors(starting_color, ending_color, height)

            for i in range(pixels_to_loop_on):
                pixel_to_set = id_list[i] if id_list else i
                strip.setPixelColor(pixel_to_set, color)
            strip.show()

            time.sleep(wait_ms / 1000.0)


def setup_lights_from_configuration(strands_config=None, set_lights_on=True):
    # Expects that light strips have been configured, then sets starting colors and animations
    if not strands_config:
        strands_config = config.settings.get('strands')
    light_data = []
    mode_list = []
    
    strand_id = 0
    for strand_name in strands_config:
        config.log.info("Setting up default lights for strand - {}".format(strand_name))
        strand = config.light_strips[strand_id]
        data = strands_config.get(strand_name)
        ids_data = data.get('ids', [])
        id_ranges_data = data.get('id_ranges', [])

        led_database = []
        for i in range(strand.numPixels()):
            led_database.append({})

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
                if anim not in mode_list:
                    mode_list.append(anim)

            for led_num in id_list:
                led = int(led_num)
                if led < strand.numPixels():
                    picked_color = color_from_list_with_range(parsed_anim)
                    if set_lights_on:
                        strand.setPixelColor(led, picked_color)
                    led_database[led] = {
                        'id': led, 'color': picked_color, 'name': id_range_data_name, 'anim_text': default_anim
                    }
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

            for anim in animations:
                if anim not in mode_list:
                    mode_list.append(anim)

        # config.log.info("- Strand {} - Pixels: {} - color: {}".format(strand_name, ids_data, default_color))
        strand_id += 1
        if set_lights_on:
            strand.show()
        light_data.append(led_database)

        config.animation_modes = mode_list
    return light_data


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
