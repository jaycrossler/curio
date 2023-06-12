#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Curio LED Manager and animation server, responds to web and MQTT traffic.

Long-running processes are tracked in a queue, and should be stopped both by killing
and from within the process.

"""
import os
import logger
from yaml import safe_load

from flask import Flask
from flask_mqtt import Mqtt
from flask_debugtoolbar import DebugToolbarExtension
import flask_monitoringdashboard as dashboard

from functions import initialize_lighting

__author___ = "Jay Crossler"
__status__ = "Development"
app_name = "Curio LED Manager"

# TODO: Have "groups" of lights that will work across multiple strings and configs
# TODO: Have a web page that modifies light groups, then assigns states and animations to them
# TODO: Have an audio manager to also have sounds

log = logger.get_logger(app_name)
mqtt_client = Mqtt()
settings = {}

app = Flask(app_name)

def initialize():
    """Load settings, set up app, and build mqtt routes
    """
    global app, mqtt_client, settings

    filename = 'config.yaml'
    if os.path.exists(filename):
        with open(filename, 'r') as conf_file:
            _yaml_contents = safe_load(conf_file)
            settings = merge_dictionaries(settings, _yaml_contents)
            log.info("Settings loaded")

    filename = 'secrets.yaml'
    if os.path.exists(filename):
        with open(filename, 'r') as conf_file:
            _yaml_secrets = safe_load(conf_file)
            settings = merge_dictionaries(settings, _yaml_secrets)
            log.info("Secrets loaded")

    app.debug = True
    app.config['MQTT_BROKER_URL'] = settings['mqtt_broker_url']
    app.config['MQTT_USERNAME'] = settings['mqtt_username']  # Set this item when you need to verify username and password
    app.config['MQTT_PASSWORD'] = settings['mqtt_password']  # Set this item when you need to verify username and password
    app.config['MQTT_BROKER_PORT'] = settings['mqtt_broker_port']
    app.config['MQTT_KEEPALIVE'] = settings['mqtt_keepalive']  # Set KeepAlive time in seconds
    app.config['MQTT_TLS_ENABLED'] = settings['mqtt_tls_enabled']  # If your broker supports TLS, set it True
    app.config['SECRET_KEY'] = settings['flask_secret_key'] # Enable flask session cookies

    # MQTT handling
    mqtt_client = Mqtt(app)
    @mqtt_client.on_connect()
    def handle_connect(client, userdata, flags, rc):
        if rc == 0:
            log.info('MQTT Connected successfully')
            mqtt_client.subscribe(settings['mqtt_listening_topic'])
        else:
            log.error('Bad MQTT connection, code:', rc)

    @mqtt_client.on_message()
    def handle_mqtt_message(client, userdata, message):
        routes.handle_mqtt_message(message, log, settings)

    @mqtt_client.on_log()
    def handle_logging(client, userdata, level, buf):
        if level == 16:
            # TODO: Have a visual green/red light on page if MQTT is working
            if buf != 'Sending PINGREQ' and buf != 'Received PINGRESP':
                log.info(buf)
        else:
            log.error(buf)
    # End MQTT Handling

    # Set up web page helpers
    DebugToolbarExtension(app)
    dashboard.bind(app)
    import routes # This is a bit of a hack, just breaks the main page up into multiple pages


def merge_dictionaries(source, destination):
    # """
    # from: https://stackoverflow.com/questions/20656135/python-deep-merge-dictionary-data
    #
    # >>> a = { 'first' : { 'all_rows' : { 'pass' : 'dog', 'number' : '1' } } }
    # >>> b = { 'first' : { 'all_rows' : { 'fail' : 'cat', 'number' : '5' } } }
    # >>> merge(b, a) == { 'first' : { 'all_rows' : { 'pass' : 'dog', 'fail' : 'cat', 'number' : '5' } } }
    # True
    # """
    for key, value in source.items():
        if isinstance(value, dict):
            # get node or create one
            node = destination.setdefault(key, {})
            merge_dictionaries(value, node)
        else:
            destination[key] = value

    return destination


# Initial application launcher
def start_flask_app():
    try:
        mqtt_client.init_app(app)
        app.run(
            use_reloader=False,
            debug=app.debug,
            host='0.0.0.0',
            port=5000,
            threaded=True)

    except Exception as e:
        log.error("Failed to start FLASK app: " + str(e))
        exit()
    except KeyboardInterrupt:
        log.warn("KeyboardInterrupt")
        exit()
    log.info("FLASK app started")
# End Launcher


if __name__ == '__main__':
    initialize()
    initialize_lighting(settings)
    start_flask_app()