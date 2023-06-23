

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


def clamp(val, minval, maxval):
    if val < minval:
        return minval
    if val > maxval:
        return maxval
    return val


def blend_colors(c1, c2, percentage):
    # c1 and c2 should be Color RGBW objects; perc should be from 0..1
    r = ((c1.r * (1-percentage)) + (c2.r * percentage))
    g = ((c1.g * (1-percentage)) + (c2.g * percentage))
    b = ((c1.b * (1-percentage)) + (c2.b * percentage))
    return Color(int(r), int(g), int(b))


def color_str(color):
    return "{:0=3d}/{:0=3d}/{:0=3d}".format(color.r, color.g, color.b)


def merge_dictionaries(source, destination):
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