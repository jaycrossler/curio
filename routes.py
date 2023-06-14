#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Curio LED Manager routes

Sets up MQTT channels and app routes (to handle Flask page requests)
Puts long-running tasks into processes that can be tracked and killed

"""

from __main__ import app, mqtt_client
from functions import func_rainbow, func_color, func_clear, get_status
from multiprocessing import Process
from flask import render_template, request

import config
import os
from colour import Color as Colour

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
    if mqtt_client:
        mqtt_client.publish(config.setting('mqtt_publish_mode_topic'), mode)
    return "Trying to run action mode {}".format(mode)


# ----------------------------
@app.route("/rainbow", methods=["GET"])
def rainbow_view():
    msg = "Rainbow process called, {} strips total".format(len(config.light_strips))

    start_new_animation(msg)
    for light_strip in config.light_strips:
        start_process(func_rainbow, msg, light_strip)
    return msg


@app.route("/blue", methods=["GET"])
def blue_view():
    msg = "Color: Blue"
    start_new_animation(msg)
    func_color(0, 0, 255)
    return msg


@app.route("/red", methods=["GET"])
def red_view():
    msg = "Color: Red"
    start_new_animation(msg)
    func_color(255, 0, 0)
    return msg


@app.route("/green", methods=["GET"])
def green_view():
    msg = "Color: Green"
    start_new_animation(msg)
    func_color(0, 255, 0)
    return msg


@app.route('/rgb', methods=['POST'])
def rgb():
    r = int(request.form['red'])
    g = int(request.form['green'])
    b = int(request.form['blue'])
    msg = "Color: RGB: ({}, {}, {})".format(r, g, b)

    start_new_animation(msg)
    func_color(r, g, b)
    return msg


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
    return msg


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
    return msg


@app.route("/all off", methods=["GET"])
def off_view():
    msg = "Colors Off"
    start_new_animation(msg)
    func_clear()
    return msg


@app.route('/colors')
def get_colors():
    output = ""
    strip_num = 0
    for strip in config.light_strips:
        strip_num += 1
        strip_html = ""
        for led in range(strip.numPixels()):
            pixel = strip.getPixelColorRGB(led)
            color = Colour(rgb=(pixel.r / 255.0, pixel.g / 255.0, pixel.b / 255.0))
            hex_color = color.hex
            strip_html += "<span style='color:{}'>⬤</span>".format(hex_color)
        output += "<div>{}:{}</div>".format(strip_num, strip_html)
    return output


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
