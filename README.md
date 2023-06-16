# Curio - LED Manager and animation server
Raspberry Pi light, animation, and sound manager that is controllable from Remotes, buttons, Web, and via MQTT
(Great for control via Home Assistant).

Soon to have default support for Alexa and Google Home.

# Notes
Long-running processes are tracked in a queue, and should be stopped both by killing
and from within the process.

# TODOs:
- TODO: Rebuild simpler standard settings interface
- TODO: Have a web page that modifies light groups, then assigns states and animations to them
- TODO: Have an audio manager to also have sounds
- TODO: Build Alexa driver

# Instructions:
- Log into Raspi (ideally via ssh or plug in monitor and keyboard)
- git clone https://github.com/jaycrossler/curio.git
- sudo -H pip3 install --upgrade pip
- pip3 install virtualenv virtualenvwrapper (takes a while)
- Add to .bashrc the virtualenv lines as described in: https://raspberrypi-guide.github.io/programming/create-python-virtual-environment
- mkvirtualenv dev
- workon dev
- cd curio
- create settings.yaml
- sudo python3 -m pip install -r requirements.txt
- These are:  python3 -m pip install pyyaml flask flask_mqtt flask_debugtoolbar flask_monitoringdashboard rpi_ws281x
- sudo python3 app.py