#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Curio LED Manager routes

Sets up MQTT channels and app routes (to handle Flask page requests)
Puts long-running tasks into processes that can be tracked and killed

"""
import json
from __main__ import app, mqtt_client
from functions import func_rainbow, func_color, func_clear, get_status, setup_lights_from_configuration
from multiprocessing import Process
from flask import render_template, request

import config
import os
from colour import Color as Colour, RGB_TO_COLOR_NAMES

running_processes = []
use_processes = True  # Set to False for testing processese, but messes up animations


def handle_mqtt_message(message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )
    payload = data['payload']
    topics = data['topic'].split(config.setting('mqtt_listening_topic').replace('#', ''))
    if len(topics) > 1:
        topic = topics[1]
    else:
        topic = data['topic']

    config.log.info('Received MQTT message on topic: {} with payload: {}'.format(topic, payload))

    if payload == 'clear':
        off_view()
    elif payload.startswith('mode'):
        message = payload.split(":")
        if len(message) > 1:
            mode = message[1]
            action_mode(mode)
    elif topic == "color" or topic == "":
        rgb_array = payload.split(",")
        if len(rgb_array) == 3:
            if float(rgb_array[0]) > 1 or float(rgb_array[1]) > 1 or float(rgb_array[2]) > 1:
                # Change to 0..1 not 0..255
                payload = "{},{},{}".format(float(rgb_array[0])/255, float(rgb_array[1])/255, float(rgb_array[2])/255)
            rgb_string(payload)
        else:
            rgb_color(payload)
    else:
        config.log.debug("Unrecognized topic route sent: {}".format(topic))


# Web route pages
@app.route("/", methods=['GET', 'POST'])
def index():
    config.log.info("User is browsing start page")
    return render_template("index.html", status=get_status().upper())


# TODO: Remove
@app.route("/service", methods=['GET'])
def service():
    config.log.info("User is browsing service page")
    return render_template("service.html")


@app.route("/mode/<string:mode>/", methods=["GET"])
def action_mode(mode):
    config.log.info("Action Mode set to {}".format(mode))
    config.current_mode = mode
    if mqtt_client:
        mqtt_client.publish(config.setting('mqtt_publish_mode_topic'), mode)
    setup_lights_from_configuration()
    return "Trying to run action mode {}".format(mode)


# ----------------------------
@app.route("/rainbow", methods=["GET"])
def rainbow_view():
    msg = "Rainbow process called, {} strips total".format(len(config.light_strips))

    start_new_animation(msg)
    for light_strip in config.light_strips:
        start_process(func_rainbow, msg, light_strip)
    return msg + "<br/> " + get_colors()


@app.route('/rgb', methods=['POST'])
def rgb():
    r = int(request.form['red'])
    g = int(request.form['green'])
    b = int(request.form['blue'])
    msg = "Color: RGB: ({}, {}, {})".format(r, g, b)

    start_new_animation(msg)
    func_color(r, g, b)
    return msg + "<br/> " + get_colors()


@app.route('/rgb/<string:rgb_text>')
def rgb_string(rgb_text):
    rgb_values = rgb_text.split(",")
    if not len(rgb_values) == 3:
        return "Invalid format entered, use something like: /rgb/255,100,50. Invalid: {}".format(rgb_text)

    r = float(rgb_values[0])
    g = float(rgb_values[1])
    b = float(rgb_values[2])

    if 0 <= r <= 1.0 and 0 <= g <= 1.0 and 0 <= b <= 1.0:
        r = r * 255
        g = g * 255
        b = b * 255

    r = int(r)
    g = int(g)
    b = int(b)
    msg = "Color: RGB: ({}, {}, {}) from text({})".format(r, g, b, rgb_text)

    start_new_animation(msg)
    func_color(r, g, b)
    return msg + "<br/> " + get_colors()


@app.route('/color/<string:color_text>')
def rgb_color(color_text):
    try:
        rgb_values = Colour(color_text)
        r = int(rgb_values.red * 255)
        g = int(rgb_values.green * 255)
        b = int(rgb_values.blue * 255)
        msg = "Color: RGB: ({}, {}, {}) from text({})".format(r, g, b, color_text)

        start_new_animation(msg)
        func_color(r, g, b)
    except ValueError:
        msg = "Unrecognized Color: {}".format(color_text)
    return msg + "<br/>" + get_colors()


@app.route("/all off", methods=["GET"])
def off_view():
    msg = "Colors Off"
    start_new_animation(msg)
    func_clear()
    return msg + "<br/> " + get_colors()


@app.route("/defaults", methods=["GET"])
def defaults_view():
    msg = "Default Animation"
    config.current_mode = 'default'
    start_new_animation(msg)
    func_clear()
    config.light_data = setup_lights_from_configuration(None)
    return msg + "<br/> " + get_colors()


@app.route('/mqtt_status')
def get_mqtt_status():
    msg = 'not initialized'
    if config.mqtt_initialized:
        msg = 'connected' if config.mqtt_working else 'disconnected'
    return msg


@app.route('/state')
def get_state():
    # TODO: Add CPU stats, current_mode, details on each light, etc
    state_obj = {
        'mqtt_status': get_mqtt_status(),
        'animations_running': len(running_processes),
        'strands': get_strands_as_json(),
        'mode': config.current_mode,
        'modes': config.animation_modes
    }

    return json.dumps(state_obj)


@app.route('/colors_as_html')
def get_colors():
    output = "<br/>"
    strip_num = 0
    for strip in config.light_strips:
        strip_num += 1
        strip_html = ""
        for led in range(strip.numPixels()):
            pixel = strip.getPixelColorRGB(led)
            color = Colour(rgb=(pixel.r / 255.0, pixel.g / 255.0, pixel.b / 255.0))
            hex_color = color.hex
            strip_html += "<span style='color:{}' title='Strip {}, LED {}'>⬤</span>".format(hex_color, strip_num, led)
            if led % 40 == 39:
                strip_html += " "  # Add a space every 40 lights
        output += "<div>{}:{}</div>".format(strip_num, strip_html)
    return output


def get_strands_as_json():
    output_obj = []
    strip_num = 0
    for strand_name in config.settings['strands']:
        strand_info = config.settings['strands'][strand_name]
        strip = config.light_strips[strip_num]
        info = {'strand_name': strand_name, 'strand_info': strand_info}
        led_info = []

        for led in range(strip.numPixels()):
            pixel = strip.getPixelColorRGB(led)
            color = Colour(rgb=(pixel.r / 255.0, pixel.g / 255.0, pixel.b / 255.0))
            hex_color = color.hex
            led_database_info = config.light_data[strip_num][led]
            led_group_name = led_database_info['name'] if 'name' in led_database_info else '<not set>'
            animation_text = led_database_info['anim_text'] if 'anim_text' in led_database_info else '<not set>'
            led_info.append({'color': hex_color, 'name': led_group_name, 'animation_text': animation_text})

        info['led_info'] = led_info
        output_obj.append(info)
        strip_num += 1

    return output_obj


# ------------------
@app.route("/shutdown <param>", methods=["GET"])
def shutdown(param):
    stop_everything()
    msg = "Device shut down with parameter: " + param
    config.log.info(msg)
    os.system('sudo shutdown ' + param)


@app.route("/reboot", methods=["GET"])
def reboot():
    stop_everything()
    msg = "Device reboot"
    config.log.info(msg)
    os.system('sudo reboot')


# Helpers
def start_new_animation(log_message, mqtt_message=None):
    if not mqtt_message:
        mqtt_message = log_message
    stop_everything()
    config.log.info(log_message)
    if mqtt_client:
        mqtt_client.publish(config.setting('mqtt_publish_topic'), mqtt_message)


# Process handling
def start_process(ftarget, fname, arg=None):
    try:
        if use_processes:
            global running_processes
            proc = Process(target=ftarget, name=fname, args=(arg,))
            config.log.info('Start and append to process list: {} with argument {}'.format(proc.name, arg))
            running_processes.append(proc)
            proc.daemon = True
            proc.start()
        else:
            # Run directly without adding a process
            ftarget(arg)
            proc = None

        return proc
    except Exception as e:
        config.log.error("Failed to start process " + fname + ': ' + str(e))


def stop_everything():
    global running_processes
    if len(running_processes):
        config.log.info("Stopping long processes: {}".format(len(running_processes)))

        for p in running_processes:
            config.log.debug("Stopping " + p.name)
            running_processes.remove(p)
            p.kill()
            p.join()
