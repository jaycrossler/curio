

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
    r = 255 * ((c1.r * (1-percentage)) + (c2.r * percentage))
    g = 255 * ((c1.g * (1-percentage)) + (c2.g * percentage))
    b = 255 * ((c1.b * (1-percentage)) + (c2.b * percentage))
    return Color(int(r), int(g), int(b))


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
