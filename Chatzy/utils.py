"""
    Utils file for Chatzy Talos
"""


class Color:

    __slots__ = ("_color",)

    BLACK = 0x000000
    RED = 0xFF0000
    GREEN = 0x00FF00
    BLUE = 0x0000FF
    WHITE = 0xFFFFFF

    def __init__(self, value):
        self._color = 0
        self.color = value

    def __str__(self):
        return self.color[2:]

    def __eq__(self, other):
        return self._color == other._color

    @property
    def color(self):
        string = hex(self._color)
        if len(string) < 8:
            string += "0" * (8 - len(string))
        return string

    @color.setter
    def color(self, value):
        if value is None:
            self._color = 0
        elif isinstance(value, str):
            try:
                num = int(value, 16)
            except ValueError:
                raise ValueError("Color string must be a hex literal")
            if num > 0xFFFFFF or num < 0x0:
                raise ValueError("Color must be between 0x000000 and 0xFFFFFF")
            self._color = num
        elif isinstance(value, int):
            if value > 0xFFFFFF or value < 0x0:
                raise ValueError("Color must be between 0x000000 and 0xFFFFFF")
            self._color = value
        elif isinstance(value, Color):
            self._color = value._color
        else:
            raise TypeError("Cannot convert that type to color")
