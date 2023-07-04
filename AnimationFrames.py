from includes import *
from config import log
from itertools import chain, cycle
from math import sin, pi


class RainbowFrame:
    """Have pixels rotate colors through a 'wheel' rainbow pattern """
    def __init__(self, strip, strip_id, pixel_ids=None, config=None):
        super(RainbowFrame, self).__init__()

        self._pixels_count = len(pixel_ids) if pixel_ids else strip.numPixels()
        self._strip = strip
        self._strip_id = strip_id
        self._pixel_ids = pixel_ids
        self._config = config if config else {}
        self._j = 0

        speed = config.get('loop_speed', 3)
        self._delay = remap(1, 6, 40, 1, speed)  # measured in 10ms steps (from 1 to 40)

    @property
    def delay_between_frames(self):
        # number of 10ms increments to delay before next animation frame should be called
        return int(self._delay) if self._delay else 5

    @property
    def strip(self):
        return self._strip

    @property
    def strip_id(self):
        return self._strip_id

    def next(self):
        # For the next frame, shift each color by 1 in the 'wheel' of colors, rotating by 256
        self._j += 1
        self._j %= 256

        for i in range(self._pixels_count):
            pixel_to_set = self._pixel_ids[i] if self._pixel_ids else i
            color = wheel((int(i * 256 / self._pixels_count) + self._j) & 255)
            self._strip.setPixelColor(pixel_to_set, color)


class WarpFrame:
    """Pulse pixels repeatedly in a sine wave pattern where the center moves towards
     ending_color and back repeatedly """

    def __init__(self, strip, strip_id, pixel_ids=None, config=None):
        super(WarpFrame, self).__init__()

        self._pixels_count = len(pixel_ids) if pixel_ids else strip.numPixels()
        self._strip = strip
        self._strip_id = strip_id
        self._pixel_ids = pixel_ids
        self._config = config if config else {}

        self._speed = speed = config.get('loop_speed', 3)
        self._delay = remap(1, 6, 8, 1, speed)  # measured in 10ms steps

        # Animation Specific variables
        self._provided_colors = config.get('color_list', [])
        self._starting_color = self._provided_colors[0] if len(self._provided_colors) > 0 else Color(0, 0, 255)
        self._ending_color = self._provided_colors[1] if len(self._provided_colors) > 1 else Color(255, 255, 255)
        self._pulse_height = config.get('pulse_height', 50)

        # Build an iterable set of numbers that cycles from 1..50..1..50..1, etc
        self._height_matrix = cycle(chain(range(0, self._pulse_height), range(self._pulse_height, 0, -1)))

    @property
    def delay_between_frames(self):
        # number of 10ms increments to delay before next animation frame should be called
        return int(self._delay) if self._delay else 5

    @property
    def strip(self):
        return self._strip

    @property
    def strip_id(self):
        return self._strip_id

    def next(self):
        # Loop through each pixel and blend it toward the target color
        height_of_pulse = self._height_matrix.__next__()  # Move the height closer or farther in its cycle

        for i in range(self._pixel_ids):
            pixel_to_set = self._pixel_ids[i] if self._pixel_ids else i

            # Note on math: .5*pi = 1, 1.5*pi = -1.  So sin(x + .5pi) + 1 ranges from 0to2 and 0to2pi
            # .5*(sin((2*pi*x) - (.5*pi))+1) goes from 0to1 and 0to1
            x_range = (i + .5) / (self._pixels_count + 1)  # Set it so the first is always a little into the color mix
            amplitude_of_point = .5 * (sin((2 * pi * x_range) - (.5 * pi)) + 1)
            y_range = height_of_pulse / self._pulse_height

            color = blend_colors(self._starting_color, self._ending_color, amplitude_of_point * y_range)
            self._strip.setPixelColor(pixel_to_set, color)


class TwinkleFrame:
    def __init__(self, strip, strip_id, pixel_ids=None, config=None):
        super(TwinkleFrame, self).__init__()

        self._pixels_count = len(pixel_ids) if pixel_ids else strip.numPixels()
        self._strip = strip
        self._strip_id = strip_id
        self._pixel_ids = pixel_ids
        self._config = config if config else {}

        self._speed = speed = config.get('loop_speed', 3)
        self._delay = remap(1, 6, 12, 1, speed)  # measured in 10ms steps (from 1 to 40)

        # Animation Specific variables
        self._provided_colors = config.get('color_list', [])
        self._color_variations = config.get('color_variations', [])
        if len(self._provided_colors) < 1:
            self._provided_colors.append(Color(200, 200, 0))
        if len(self._provided_colors) < 2:
            self._provided_colors.append(Color(247, 218, 76))

        self._max_animation_amount = 2 + (5 * speed)  # Should be greater than 2 at least
        self._chance_to_increase_brightness = .05
        self._chance_to_change_colors = .05
        self._chance_to_start_a_twinkle = float(config.get('density', .3))
        self._speed_to_blend = .05
        self._twinkle_variance = .2

        # Have a list for each pixel to show what percentage it's animated and color
        self._led_status_list = []
        self._led_color_list = []
        for i in range(pixel_ids):
            self._led_status_list.append(0)

            # set all pixels to a random appropriate starting color
            starting_color = random_color_with_range_from_list(self._provided_colors, self._color_variations,
                                                               self._twinkle_variance)
            self._led_color_list.append(starting_color)
            pixel_to_set = pixel_ids[i] if pixel_ids else i
            strip.setPixelColor(pixel_to_set, starting_color)

    @property
    def delay_between_frames(self):
        # number of 10ms increments to delay before next animation frame should be called
        return int(self._delay) if self._delay else 5

    @property
    def strip(self):
        return self._strip

    @property
    def strip_id(self):
        return self._strip_id

    def next(self):
        # Loop through each pixel and randomly blend it towards a target color
        for i in range(self._pixels_count):
            current_color = "unset"
            current_color_target = "unset"
            try:
                pixel_to_set = self._pixel_ids[i] if self._pixel_ids else i
                current_color = self._strip.getPixelColorRGB(pixel_to_set)
                current_color_target = self._led_color_list[i]
                current_animation_amount = self._led_status_list[i]

                # Use a state machine (tracked by current_animation_amount) for how each pixel is animating
                if current_animation_amount >= self._max_animation_amount:  # It passed the goal, start de-animating it
                    # Make it negative to show that it should decrease
                    self._led_status_list[i] *= -1
                    current_color = blend_colors(current_color, current_color_target, self._speed_to_blend)
                elif (2 + self._speed / 2) < current_animation_amount < self._max_animation_amount:
                    current_color = blend_colors(current_color, current_color_target, self._speed_to_blend)
                    # Usually increase the brightness towards the target, but sometimes don't
                    if random.random() < self._chance_to_increase_brightness:
                        self._led_status_list[i] /= 2
                    else:
                        self._led_status_list[i] += random.random()

                    if random.random() < self._chance_to_change_colors:
                        self._led_color_list[i] = random_color_with_range_from_list(self._provided_colors,
                                                                                    self._color_variations,
                                                                                    self._twinkle_variance)

                elif 0 < current_animation_amount:  # It started animating, don't mess with it
                    self._led_status_list[i] += random.random()
                    current_color = blend_colors(current_color, current_color_target, self._speed_to_blend)
                elif current_animation_amount == 0:  # It is not animating
                    # Set it towards the target
                    if random.random() < (self._chance_to_start_a_twinkle**2):
                        self._led_status_list[i] += random.random()
                        new_color = random_color_range(current_color, self._twinkle_variance)
                        self._led_color_list[i] = new_color
                        current_color = Color(255, 255, 255)
                elif current_animation_amount > (-1 - self._speed / 2):  # It's close enough to 0, end the animation
                    self._led_status_list[i] = 0
                    current_color = current_color_target
                else:  # It's negative, so should approach back to 0
                    self._led_status_list[i] += random.random()
                    current_color = blend_colors(current_color, current_color_target, self._speed_to_blend)

                self._strip.setPixelColor(pixel_to_set, current_color)

            except AttributeError as e:
                log.warn("Color error: current:{} target:{}. {}".format(current_color, current_color_target, e))


class PulseFrame:
    """Pulse pixels repeatedly in a sine wave pattern where the center moves towards
     ending_color and back repeatedly """

    def __init__(self, strip, strip_id, pixel_ids=None, config=None):
        super(PulseFrame, self).__init__()

        self._pixels_count = len(pixel_ids) if pixel_ids else strip.numPixels()
        self._strip = strip
        self._strip_id = strip_id
        self._pixel_ids = pixel_ids
        self._config = config if config else {}

        self._speed = speed = config.get('loop_speed', 3)
        self._delay = remap(1, 6, 6, 1, speed)  # measured in 10ms steps (from 1 to 40)

        # Animation Specific variables
        self._provided_colors = config.get('color_list', [])
        self._starting_color = self._provided_colors[0] if len(self._provided_colors) > 0 else Color(0, 0, 0)
        self._ending_color = self._provided_colors[1] if len(self._provided_colors) > 1 else Color(255, 255, 255)

        self._color_variations = config.get('color_variations', [])
        self._pulse_height = config.get('pulse_height', 50)
        self._mode = config.get('mode', 'linear')
        self._iteration = 0

        # Build an iterable set of numbers that cycles from 1..50..1..50..1, etc
        self._height_matrix = cycle(chain(range(0, self._pulse_height), range(self._pulse_height, 0, -1)))

    @property
    def delay_between_frames(self):
        # number of 10ms increments to delay before next animation frame should be called
        return int(self._delay) if self._delay else 5

    @property
    def strip(self):
        return self._strip

    @property
    def strip_id(self):
        return self._strip_id

    def next(self):
        # Loop through each pixel and blend it toward the target color
        height_of_pulse = self._height_matrix.__next__()  # Move the height closer or farther in its cycle
        if height_of_pulse == 0:  # If the loop started over
            # Move to next ending color (CLEANUP: Can make this an iterable cycle for legibility)
            if len(self._provided_colors) > 1:
                self._ending_color = self._provided_colors[(self._iteration + 1) % len(self._provided_colors)]
            self._iteration += 1

        # Determine 'height' or how bright the pulse is, depending on the blending mode
        height = height_of_pulse / self._pulse_height
        if self._mode == 'sin':
            height = .5 * (1 + sin((1.5 + height) * pi))
        elif self._mode == 'spike':
            regular_sin = .5 * (1 + sin((2 * pi * height) + (1.5 * pi)))  # maps to 0..1/0..1
            if regular_sin > 0:
                regular_sin = (regular_sin ** -2)
                # TODO: Spikes, but has some weird side values
            height = 2 - regular_sin  # make it thinner and spikey, then only take if positive
            if height < 0:
                height = 0
        elif self._mode == 'linear':
            pass  # use base height

        # Determine the color
        color = blend_colors(self._starting_color, self._ending_color, height)

        # Set all pixels to that color
        for i in range(self._pixels_count):
            pixel_to_set = self._pixel_ids[i] if self._pixel_ids else i
            self._strip.setPixelColor(pixel_to_set, color)


class BlinkFrame:
    """Blink pixels repeatedly through each color in list """

    def __init__(self, strip, strip_id, pixel_ids=None, config=None):
        super(BlinkFrame, self).__init__()

        self._pixels_count = len(pixel_ids) if pixel_ids else strip.numPixels()
        self._strip = strip
        self._strip_id = strip_id
        self._pixel_ids = pixel_ids
        self._config = config if config else {}

        self._speed = speed = config.get('loop_speed', 3)
        self._delay = remap(1, 6, 200, 10, speed)  # measured in 10ms steps
        self._iteration = 0

        # Animation Specific variables
        self._provided_colors = config.get('color_list', [])
        if len(self._provided_colors) < 1:
            self._provided_colors.append(Color(255, 255, 255))
        if len(self._provided_colors) < 2:
            self._provided_colors.append(Color(0, 0, 0))

    @property
    def delay_between_frames(self):
        # number of 10ms increments to delay before next animation frame should be called
        return int(self._delay) if self._delay else 5

    @property
    def strip(self):
        return self._strip

    @property
    def strip_id(self):
        return self._strip_id

    def next(self):
        # Set all pixels to next color in sequence
        color = self._provided_colors[self._iteration % len(self._provided_colors)]

        # Set all pixels to that color
        for i in range(self._pixels_count):
            pixel_to_set = self._pixel_ids[i] if self._pixel_ids else i
            self._strip.setPixelColor(pixel_to_set, color)

        self._iteration += 1


class BlinkenlichtFrame:
    """Blink pixels through each color in list in a slow on/off style, supporting randomness """

    def __init__(self, strip, strip_id, pixel_ids=None, config=None):
        super(BlinkenlichtFrame, self).__init__()

        self._pixels_count = len(pixel_ids) if pixel_ids else strip.numPixels()
        self._strip = strip
        self._strip_id = strip_id
        self._pixel_ids = pixel_ids
        self._config = config if config else {}

        self._speed = speed = config.get('loop_speed', 3)
        self._delay = remap(1, 6, 12, 1, speed)  # measured in 10ms steps (from 1 to 40)

        # Animation Specific variables
        self._provided_colors = config.get('color_list', [])
        self._color_variations = config.get('color_variations', [])
        if len(self._provided_colors) < 1:
            self._provided_colors.append(Color(0, 0, 0))
        if len(self._provided_colors) < 2:
            self._provided_colors.append(Color(247, 218, 76))
        self._starting_color = self._provided_colors[0]

        self._max_animation_amount = 2 + (5 * speed)  # Should be greater than 2 at least
        self._chance_to_increase_brightness = .05
        self._chance_to_change_colors = .05
        self._chance_to_start_a_twinkle = float(config.get('density', .3))
        self._speed_to_blend = 2 / self._max_animation_amount
        self._iteration = 0
        self._mode = config.get('mode', 'linear')

        # Have a list for each pixel to show what percentage it's animated and color
        self._led_status_list = []
        self._led_color_list = []

        # set all pixels to starting color
        for i in range(pixel_ids):
            self._led_status_list.append(0)
            self._led_color_list.append(self._starting_color)
            pixel_to_set = pixel_ids[i] if pixel_ids else i
            strip.setPixelColor(pixel_to_set, self._starting_color)

    @property
    def delay_between_frames(self):
        # number of 10ms increments to delay before next animation frame should be called
        return int(self._delay) if self._delay else 5

    @property
    def strip(self):
        return self._strip

    @property
    def strip_id(self):
        return self._strip_id

    def next(self):
        # Loop through each pixel and randomly blend it towards a target color

        # Loop through each pixel and randomly blend it towards a target color
        current_color = "unset"
        new_color = random_color_with_range_from_list(self._provided_colors, self._color_variations, .2)

        for i in range(self._pixels_count):
            try:
                pixel_to_set = self._pixel_ids[i] if self._pixel_ids else i
                current_color = self._strip.getPixelColorRGB(pixel_to_set)
                current_color_target = self._led_color_list[i]
                current_animation_amount = self._led_status_list[i]

                # Use a state machine (tracked by current_animation_amount) for how each pixel is animating
                if current_animation_amount >= self._max_animation_amount:  # It passed the goal, start de-animating it
                    # Make it negative to show that it should decrease
                    self._led_status_list[i] *= -1
                    current_color = blend_colors(current_color, current_color_target, self._speed_to_blend)
                elif (2 + self._speed) < current_animation_amount < self._max_animation_amount: # Moving toward target
                    if self._mode == 'linear':
                        self._led_status_list[i] += random.random()
                        current_color = blend_colors(current_color, current_color_target, self._speed_to_blend)
                    else:
                        current_color = blend_colors(current_color, current_color_target, self._speed_to_blend)
                        # Usually increase the brightness towards the target, but sometimes don't
                        if random.random() < self._chance_to_increase_brightness:
                            self._led_status_list[i] /= 2
                        else:
                            self._led_status_list[i] += random.random()

                        if random.random() < self._chance_to_change_colors:
                            self._led_color_list[i] = new_color

                    current_color = blend_colors(current_color, current_color_target, self._speed_to_blend)
                    # Usually increase the brightness towards the target, but sometimes don't
                    if random.random() < self._chance_to_increase_brightness:
                        self._led_status_list[i] /= 2
                    else:
                        self._led_status_list[i] += random.random()

                    if random.random() < self._chance_to_change_colors:
                        self._led_color_list[i] = new_color

                elif 0 < current_animation_amount:  # It started animating, don't mess with it
                    self._led_status_list[i] += random.random()
                    current_color = blend_colors(current_color, current_color_target, self._speed_to_blend)
                elif current_animation_amount == 0:  # It is not animating
                    # Set it towards the target
                    if random.random() < (self._chance_to_start_a_twinkle**2):
                        self._led_status_list[i] += random.random()
                        self._led_color_list[i] = new_color
                        current_color = blend_colors(current_color, new_color, self._speed_to_blend)
                elif current_animation_amount > (-1 - self._speed):  # It's close enough to 0, end the animation
                    self._led_status_list[i] = 0
                    self._led_color_list[i] = self._starting_color
                    current_color = self._starting_color
                else:  # It's negative, so should approach back to 0
                    self._led_status_list[i] += random.random()
                    current_color = blend_colors(current_color, self._starting_color, self._speed_to_blend)

                self._strip.setPixelColor(pixel_to_set, current_color)

            except AttributeError as e:
                log.warn("Color error: current:{} target:{}. {}".format(current_color, self._starting_color, e))

        self._iteration += 1
