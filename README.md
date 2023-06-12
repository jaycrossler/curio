# curio - LED Manager and animation server
Raspberry Pi light, animation, and sound manager that is controllable from Remotes, buttons, Web, and via MQTT

# Notes
Long-running processes are tracked in a queue, and should be stopped both by killing
and from within the process.

# TODOs:
- TODO: Have "groups" of lights that will work across multiple strings and configs
- TODO: Have a web page that modifies light groups, then assigns states and animations to them
- TODO: Have an audio manager to also have sounds
