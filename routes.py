#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Curio LED Manager routes

Sets up MQTT channels and app routes (to handle Flask page reuqests)
Puts long-running tasks into processes that can be tracked and killed

"""

from __main__ import app, mqtt_client
from functions import func_rainbow, func_color, func_clear, get_status
from multiprocessing import Process
from flask import render_template, request

import config
import os

running_processes = []


def handle_mqtt_message(message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )
    # TODO: Have an array of all commands used throughout
    config.log.info('Received MQTT message on topic: {topic} with payload: {payload}'.format(**data))
    payload = data['payload']
    if payload == 'blue':
        blue_view()
    elif payload == 'red':
        red_view()
    elif payload == 'green':
        green_view()
    elif payload == 'rainbow':
        rainbow_view()
    elif payload == 'clear':
        off_view()
    elif payload.startswith('mode'):
        message = payload.split(":")
        if len(message) > 1:
            mode = message[1]
            action_mode(mode)


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


# TODO: Have a generic color route
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


@app.route("/all off", methods=["GET"])
def off_view():
    msg = "Colors Off"
    start_new_animation(msg)
    func_clear()
    return msg


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
        global running_processes
        proc = Process(target=ftarget, name=fname, args=(arg,))
        config.log.info('Start and append to process list: {} with argument {}'.format(proc.name, arg))
        running_processes.append(proc)
        proc.daemon = True
        proc.start()
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
