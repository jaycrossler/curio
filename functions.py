#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Methods to call light effect functions

built upon: https://github.com/rpi-ws281x/rpi-ws281x-python/blob/master/examples/strandtest.py

"""
__author___ = "Jay Crossler"
__status__ = "Development"

import platform
from animations import *
import AnimationProcess

from multiprocessing import Process
from datetime import datetime

if platform.system() == 'Darwin':
    # This library doesn't import on Macintosh computers, ignore it and use a stub
    from rpi_fake import PixelStrip, Color
else:
    from rpi_ws281x import PixelStrip, Color

running_processes = []  # Database of running processes
use_processes = True  # Set to False for testing processes, but messes up animations

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


def setup_lights_from_configuration(strands_config=None, set_lights_on=True):
    # Expects that light strips have been configured, then sets starting colors and animations
    if not strands_config:
        strands_config = config.settings.get('strands')
    light_data = []
    mode_list = []

    animations_to_run_for_this_mode = []

    # Look through all data for each strand, build modes and add animations
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

        # Look at the ID_RANGES section, and parse out any modes and animations
        for id_range_data_name in id_ranges_data:
            id_range_data = id_ranges_data.get(id_range_data_name)

            ids = id_range_data.get('ids', "")
            id_start = id_range_data.get('id_start', "")
            id_end = id_range_data.get('id_end', "")
            id_list = find_ids(ids, id_start, id_end, limit_to=strand.numPixels())

            animations = id_range_data.get('animations', [])
            default_anim = animations.get(config.current_mode, 'off')
            parsed_anim = parse_animation_text(default_anim)

            # Build mode and animation details
            for anim in animations:
                if anim not in mode_list:
                    mode_list.append(anim)
                if anim == config.current_mode and parsed_anim.get('animation'):
                    anim_data = {'range_name': id_range_data_name, 'leds': id_list,
                                 'animation': animations[anim], 'strip': strand, 'strip_id': strand_id}
                    animations_to_run_for_this_mode.append(anim_data)

            # Go through all the leds in the combined ranged and listed entries
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

        # Now also look at individual LED items, and build animations and modes from those
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
                if anim == config.current_mode and parsed_anim.get('animation'):
                    anim_data = {'range_name': id_name, 'leds': [id_data_led],
                                 'animation': animations[anim], 'strip': strand, 'strip_id': strand_id}
                    animations_to_run_for_this_mode.append(anim_data)

        # config.log.info("- Strand {} - Pixels: {} - color: {}".format(strand_name, ids_data, default_color))
        strand_id += 1
        if set_lights_on:
            strand.show()
        light_data.append(led_database)

    config.animation_modes = mode_list

    if len(animations_to_run_for_this_mode) > 1:
        start_multiple_animations(animations_to_run_for_this_mode)

    return light_data


def start_multiple_animations(animation_list):

    # Stop all existing animations
    stop_everything()

    # TODO: Consider a new process for each strip?
    animation_process = AnimationProcess.AnimationProcess()

    for anim in animation_list:
        animation_text = anim.get('animation')
        id_list = anim.get('leds', [])
        range_name = anim.get('range_name')
        strip = anim.get('strip')
        strip_id = anim.get('strip_id')
        command_parsed = parse_animation_text(animation_text)
        animation_name = command_parsed.get('animation', 'unknown')

        animation_data = {'strip': strip, 'strip_id': strip_id, 'id_list': id_list, 'animation': animation_name,
                          'command': animation_text, 'command_parsed': command_parsed, 'range_name': range_name}

        animation_process.add_animation(animation_data)

    animation_process.start()
    # TODO: Check if this runs after process is killed
    config.log.info("Animation Process holding {} animations Ended".format(len(animation_list)))


# Process handling
def start_process(ftarget, fname, arg=None):
    # TODO: Check if there is an animation on that strand, if so kill existing and restart
    try:
        if use_processes:
            global running_processes
            proc = Process(target=ftarget, name=fname, args=(arg,))
            config.log.info('Start and append to process list: {} with argument {}'.format(proc.name, arg))
            running_processes.append({'process': proc, 'arguments': arg, 'started': datetime.now()})
            proc.daemon = True
            proc.start()
        else:
            # Run directly without adding a process
            ftarget(arg)
            proc = None

        return proc
    except Exception as e:
        config.log.error("Failed to start process " + fname + ': ' + str(e))


def stop_process(process_id):
    msg = ""
    global running_processes
    for p in running_processes:
        process = p.get('process')
        if process.pid == process_id:
            msg = "Stopping {} with args {}".format(process.name, p.get('arguments'))
            config.log.debug(msg)
            running_processes.remove(p)
            process.kill()
            process.join()
    return msg


def stop_everything():
    global running_processes
    if len(running_processes):
        config.log.info("Stopping long processes: {}".format(len(running_processes)))

        for p in running_processes:
            process = p.get('process')
            config.log.debug("Stopping {} with args {}".format(process.name, p.get('arguments')))
            running_processes.remove(process)
            process.kill()
            process.join()


def get_process_info_as_object():
    processes = []
    for p in running_processes:
        process = p.get('process')
        arguments = p.get('arguments')
        processes.append({'process': process.pid, 'name': process.name, 'animation': arguments.get('animation'),
                          'strand': arguments.get('strip_id'),
                          'started': p.get('started').strftime("%H:%M:%S"), 'id_list': arguments.get('id_list')})
    return processes

# -----------------------------
# Not Used:
# -----------------------------


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
