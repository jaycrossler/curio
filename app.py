#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Curio LED Manager and animation server, responds to web and MQTT traffic.

Long-running processes are tracked in a queue, and should be stopped both by killing
and from within the process.

"""
from flask import Flask
from flask_mqtt import Mqtt
from flask_debugtoolbar import DebugToolbarExtension
# import flask_monitoringdashboard as dashboard (Uses SciPy, which is hard to install, so skipped for now)

from functions import initialize_lighting, setup_lights_from_configuration
import config
from socket import gaierror

__author___ = "Jay Crossler"
__status__ = "Development"
app_name = "Curio LED Manager"

# TODO: Have "groups" of lights that will work across multiple strings and configs
# TODO: Have a web page that modifies light groups, then assigns states and animations to them
# TODO: Have an audio manager to also have sounds
# TODO: Visualize light status on webpage, ideally on top of an image

# TODO: Consider moving app and mqtt into config
mqtt_client = None
app = None


def initialize_config_and_app():
    """Load settings, set up app, and build mqtt routes
    """
    global app, mqtt_client

    app = Flask(app_name)
    config.initialize(app_name)
    app.debug = True
    try:
        url = config.settings['mqtt_broker_url']
        if not url or len(url) < 3:
            raise ValueError

        app.config['MQTT_BROKER_URL'] = url
        app.config['MQTT_USERNAME'] = config.setting('mqtt_username')
        app.config['MQTT_PASSWORD'] = config.setting('mqtt_password')
        app.config['MQTT_BROKER_PORT'] = config.setting('mqtt_broker_port', 1883)
        app.config['MQTT_KEEPALIVE'] = config.setting('mqtt_keepalive', 5)  # Set KeepAlive time in seconds
        app.config['MQTT_TLS_ENABLED'] = config.setting('mqtt_tls_enabled', False)

        # MQTT handling
        mqtt_client = Mqtt(app)

    except ValueError:
        config.log.warning('MQTT settings and secrets information was not entered, skipping MQTT')
        config.mqtt_working = False
        config.mqtt_initialized = False
    except gaierror as e:
        config.log.warning('MQTT could not connect - namespace lookup error: {}'.format(e))
        config.mqtt_working = False
        config.mqtt_initialized = False

    app.config['SECRET_KEY'] = config.setting('flask_secret_key', '1234')  # Enable flask session cookies

    if mqtt_client:
        @mqtt_client.on_connect()
        def handle_connect(client, userdata, flags, rc):
            if rc == 0:
                config.log.info('MQTT connected: client {} and data {} and flags {}'.format(client, userdata, flags))
                mqtt_client.subscribe(config.setting('mqtt_listening_topic'))
                config.mqtt_working = True
                config.mqtt_initialized = True
            else:
                config.log.error('Bad MQTT connection, code:', rc)
                config.mqtt_working = False

        @mqtt_client.on_message()
        def handle_mqtt_message(client, userdata, message):
            routes.handle_mqtt_message(message)

        @mqtt_client.on_log()
        def handle_logging(client, userdata, level, buf):
            if level == 16:
                # TODO: Have a visual green/red light on page if MQTT is working
                if buf != 'Sending PINGREQ' and buf != 'Received PINGRESP':
                    config.log.info(buf)
            else:
                config.log.error(buf)
        # End MQTT Handling

        @mqtt_client.on_disconnect()
        def disconnected(client, userdata, flags, rc):
            config.mqtt_working = False

    # Set up web page helpers
    # DebugToolbarExtension(app)
    # dashboard.bind(app)
    import routes  # This is a bit of a hack, just breaks the main page up into multiple pages


# Initial application launcher
def start_flask_app():
    try:
        if mqtt_client:
            mqtt_client.init_app(app)
        app.run(
            use_reloader=False,
            debug=app.debug,
            host='0.0.0.0',
            port=config.setting('app_port', 5000),
            threaded=True)

    except Exception as e:
        config.log.error("Failed to start FLASK app: " + str(e))
        exit()
    except KeyboardInterrupt:
        config.log.warn("KeyboardInterrupt")
        exit()
    config.log.info("FLASK app started")
# End Launcher


if __name__ == '__main__':
    initialize_config_and_app()
    initialize_lighting()
    config.light_data = setup_lights_from_configuration()
    start_flask_app()
