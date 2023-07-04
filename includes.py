#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Useful included methods and classes
"""
__author___ = "Jay Crossler"
__status__ = "Development"

import logging
import random
from colour import Color as ColourColor

animation_options = ['rainbow', 'wheel', 'pulsing', 'warp', 'blinkenlicht', 'blinking', 'twinkle']


class RGBW(int):
    def __new__(self, r, g=None, b=None, w=None):
        if (g, b, w) == (None, None, None):
            return int.__new__(self, r)
        else:
            if w is None:
                w = 0
            return int.__new__(self, (w << 24) | (r << 16) | (g << 8) | b)

    @property
    def r(self):
        return (self >> 16) & 0xff

    @property
    def g(self):
        return (self >> 8) & 0xff

    @property
    def b(self):
        return self & 0xff

    @property
    def w(self):
        return (self >> 24) & 0xff

    def __repr__(self):
        return f"RGBW({self.r}, {self.g}, {self.b})"


def Color(red, green, blue, white=0):
    """Convert the provided red, green, blue color to a 24-bit color value.
    Each color component should be a value 0-255 where 0 is the lowest intensity
    and 255 is the highest intensity.
    """
    return RGBW(red, green, blue, white)


def clamp(val, min_val, max_val):
    if val < min_val:
        return min_val
    if val > max_val:
        return max_val
    return val


def blend_colors(c1: Color, c2: Color, percentage: float) -> Color:
    # c1 and c2 should be Color RGBW objects; perc should be from 0..1
    try:
        r = ((c1.r * (1-percentage)) + (c2.r * percentage))
        g = ((c1.g * (1-percentage)) + (c2.g * percentage))
        b = ((c1.b * (1-percentage)) + (c2.b * percentage))
        output = Color(int(r), int(g), int(b))
    except AttributeError as e:
        output = Color(0, 0, 0)

    return output


def color_str(color: Color) -> str:
    return "{:0=3d}/{:0=3d}/{:0=3d}".format(color.r, color.g, color.b)


def dict_pruned(d: dict) -> dict:
    return {k: v for k, v in d.items() if (type(v) is list and len(v)) or (type(v) is not list and v is not None)}


def merge_dictionaries(source: dict, destination: dict) -> dict:
    # """
    # Sourced from: https://stackoverflow.com/questions/20656135/python-deep-merge-dictionary-data
    # """
    for key, value in source.items():
        if isinstance(value, dict):
            # get node or create one
            node = destination.setdefault(key, {})
            merge_dictionaries(value, node)
        else:
            destination[key] = value

    return destination


# From https://gist.github.com/laundmo/b224b1f4c8ef6ca5fe47e132c8deab56
def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolate on the scale given by a to b, using t as the point on that scale.

    Examples
    --------
        50 == lerp(0, 100, 0.5)
        4.2 == lerp(1, 5, 0.8)

    """
    return (1 - t) * a + t * b


def inv_lerp(a: float, b: float, v: float) -> float:
    """Inverse Linear Interpolation, get the fraction between a and b on which v resides.

    Examples
    --------
        0.5 == inv_lerp(0, 100, 50)
        0.8 == inv_lerp(1, 5, 4.2)

    """
    return (v - a) / (b - a)


def remap(i_min: float, i_max: float, o_min: float, o_max: float, v: float) -> float:
    """Remap values from one linear scale to another, a combination of lerp and inv_lerp.

    i_min and i_max are the scale on which the original value resides,
    o_min and o_max are the scale to which it should be mapped.

    Examples
    --------
        45 == remap(0, 100, 40, 50, 50)
        6.2 == remap(1, 5, 3, 7, 4.2)

    """
    return lerp(o_min, o_max, inv_lerp(i_min, i_max, v))


def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)


def find_ids(ids=None, id_start=None, id_end=None, limit_to=None):
    if ids and len(ids) > 0:
        id_list = ids.split(',')
    else:
        if id_start == 'NaN':
            id_start = None
        if id_end == 'NaN':
            id_end = None

        if type(id_start) is str and len(id_start):
            id_start = int(id_start)
        if type(id_end) is str and len(id_end):
            id_end = int(id_end)

        if type(id_start) is int and type(id_end) is int:
            id_list = range(id_start, id_end)
        else:
            id_list = []

    id_list = [int(i) for i in id_list]

    if limit_to:
        for id_num in id_list:
            if int(id_num) > limit_to:
                id_list.remove(id_num)

    return id_list


def parse_animation_text(text):
    animation = None
    loop_modifier = None
    loop_speed = None
    special = None
    color_list = []
    variation_list = []  # Color random variations that go with each color
    extras = []

    # If "off" passed in, field is set to: False, catch that with an if statement
    if text and len(text) > 3:
        # Format is 'color word(s)', 'animation', 'modifier', 'speed', 'special'
        # example: "yellow, pulsing, random" or "red and white, pulsing" or "blue:.1"
        text = text.strip().lower()

        # Break by commas into named chunks
        words = text.split(",")
        color_name = words[0]
        if color_name == 'none':
            color_name = 'blue'

        # separate out multiple colors
        colors_names = color_name.split(' and ')
        for color_name_split in colors_names:
            try:
                # parse out any : after color names for random variations, eg Blue:.1 or Pink:.2:0:.1
                color_var_split = color_name_split.split(':')
                variations = []
                if len(color_var_split) > 1:
                    variations = color_var_split[1:]

                colour_rgb = ColourColor(color_var_split[0])
                color = Color(int(colour_rgb.red * 255), int(colour_rgb.green * 255), int(colour_rgb.blue * 255))
                color_list.append(color)
                variation_list.append(variations)
            except Exception:
                print(
                    'Color "{}" not recognized from config.yaml strand animation settings'.format(color_name_split))

        # See if an animation or supporting information was entered
        if len(words) > 1:
            for word in words[1:]:
                text = word.strip().lower()
                if valid_animation(text):
                    animation = text
                elif text in ['random', 'centered', 'cycled']:
                    loop_modifier = text
                elif text in ['slow', '1', 1]:
                    loop_speed = 1
                elif text in ['gentle', '2', 2]:
                    loop_speed = 2
                elif text in ['medium', '3', 3]:
                    loop_speed = 3
                elif text in ['speedy', '4', 4]:
                    loop_speed = 4
                elif text in ['medium', '5', 5]:
                    loop_speed = 5
                elif text in ['fast', '6', 6]:
                    loop_speed = 6
                elif ':' in text:
                    # There is a variable in the text, parse it out
                    pieces = text.split(":")
                    if len(pieces) > 1:
                        var_name = pieces[0]
                        var_val = pieces[1]
                        extras.append({var_name: var_val})

    output = {'color_list': color_list, 'color_variations': variation_list, 'special': special,
              'animation': animation, 'loop_modifier': loop_modifier, 'loop_speed': loop_speed}

    if len(extras):
        for dic in extras:
            for key in dic:
                output[key] = dic[key]

    # Take out empty keys
    output = {k: v for k, v in output.items() if v is not None or (type(v) == list and len(v))}

    return output


def valid_animation(anim):
    return anim in animation_options
# TODO: Lookup functions to run


def color_from_list_with_range(parsed_animation):
    color_list = parsed_animation['color_list']
    modifier_list = parsed_animation['color_variations']

    if len(color_list):
        color_number_to_use = random.choice(range(len(color_list)))
        out_color = color_list[color_number_to_use]
        out_modifier = modifier_list[color_number_to_use] if len(modifier_list) >= color_number_to_use else []

        if len(out_modifier) > 0:
            out_color = random_color_range(out_color, out_modifier)
    else:
        out_color = 0

    return out_color


def random_color_with_range_from_list(colors, variations, default_variation=.2):
    color_i = random.randint(0, len(colors) - 1)
    color_range = variations[color_i] if len(variations) > color_i else [default_variation]
    return random_color_range(colors[color_i], color_range)


def random_color_range(color, ranges):
    # Start with a Color, then return another color close to it based on percentages in 'ranges'.
    # example: "Color(120, 100, 100), [.1]" or "Color(120, 100, 100), [.2,0,.2]"
    if type(ranges) == float:
        ranges = [ranges]
    ranges = ranges or []
    range_r = range_g = range_b = 0
    if len(ranges) > 2:
        range_b = ranges[2]
    if len(ranges) > 1:
        range_g = ranges[1]
    if len(ranges) > 0:
        range_r = ranges[0]
    if len(ranges) == 1:
        range_g = range_r
        range_b = range_r

    range_r = int(float(range_r) * 255)
    range_g = int(float(range_g) * 255)
    range_b = int(float(range_b) * 255)

    r = color.r
    g = color.g
    b = color.b

    new_r = clamp(random.randint(r - range_r, r + range_r), 0, 255)
    new_g = clamp(random.randint(g - range_g, g + range_g), 0, 255)
    new_b = clamp(random.randint(b - range_b, b + range_b), 0, 255)

    return Color(new_r, new_g, new_b)
