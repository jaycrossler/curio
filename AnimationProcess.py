import multiprocessing
from time import sleep

import AnimationFrames
import config


class AnimationProcess(multiprocessing.Process):
    def __init__(self, animations_data=None):
        super(AnimationProcess, self).__init__()

        self._continue_animating = False
        self._iteration = 0
        self._animations_frames = []

        # Add starting animations if provided
        self._animations_data = []
        if animations_data and len(animations_data):
            for anim in animations_data:
                self.add_animation(anim)

    def add_animation(self, animation_data):
        """Generic Animation controller, triggers correct animation based on options."""
        self._animations_data.append(animation_data)
        animation_config = animation_data.get('command_parsed', {})
        animation = animation_config.get('animation', None)
        light_strip = animation_data.get('strip', None)

        if animation and light_strip:
            animation_command = animation_data.get('command', {})
            strand = animation_data.get('strip_id')
            id_list = animation_data.get('id_list', [])

            status = "Adding '{}' animation on strip {} with {} LEDs".format(animation_command, strand, len(id_list))
            config.log.info(status)

            animation_object = None
            if animation == 'rainbow':
                animation_object = AnimationFrames.RainbowFrame(light_strip, strand, id_list, animation_config)
            elif animation == 'warp':
                animation_object = AnimationFrames.WarpFrame(light_strip, strand, id_list, animation_config)
            elif animation == 'pulsing':
                animation_object = AnimationFrames.PulseFrame(light_strip, strand, id_list, animation_config)
            elif animation == 'blinking':
                animation_object = AnimationFrames.BlinkFrame(light_strip, strand, id_list, animation_config)
            elif animation == 'blinkenlicht':
                animation_object = AnimationFrames.BlinkenlichtFrame(light_strip, strand, id_list, animation_config)
            elif animation == 'twinkle':
                animation_object = AnimationFrames.TwinkleFrame(light_strip, strand, id_list, animation_config)

            else:
                # TODO: Add more
                pass

            if animation_object:
                self._animations_frames.append(animation_object)

    def run(self):
        """Cycles through each animation, and if it's time interval has come up, run the next frame """
        # animation_data = {'strip': strip, 'strip_id': strip_id, 'id_list': id_list, 'animation': animation_name,
        #                  'command': animation_text, 'command_parsed': command_parsed, 'range_name': range_name}

        config.log.info('Animations starting')
        # Start the animation loop
        self._continue_animating = True
        while self._continue_animating:
            self._iteration += 1

            # Get the next frame from any animation that should trigger based on the time delay
            strips_shown = []
            for anim in self._animations_frames:
                if self._iteration % anim.delay_between_frames == 0:
                    anim.next()
                    if anim.strip not in strips_shown:
                        strips_shown.append(anim.strip)

            # Show the next step in each light strip that was changed
            for strip in strips_shown:
                strip.show()

            sleep(0.01)  # Sleep 10 ms

        print('AnimationProcess with {} animations halted'.format(len(self._animations_data)))

    def halt(self):
        self._continue_animating = False
