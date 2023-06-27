import os
import logger
from yaml import safe_load
from includes import merge_dictionaries

# Configuration Variables that are accessed by other scripts
light_strips = []
light_data = []
animation_modes = []
current_mode = 'default'
settings = {}
mqtt_initialized = False
mqtt_working = False
log = logger.get_logger('App')


def initialize(app_name):
    global log, settings
    log = logger.get_logger(app_name)

    if not os.path.exists('logs'):
        # If logs directory doesn't exist, create it
        os.makedirs('logs')

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

    if 'strands' not in settings:
        settings['strands'] = []


def setting(name, default_if_blank=None):
    if name in settings:
        val = settings[name]
        return val or default_if_blank
    else:
        if default_if_blank:
            return default_if_blank
        else:
            log.error('SETTING MISSING: {}'.format(name))
