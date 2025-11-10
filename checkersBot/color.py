from numpy import array

_red = "\033[31m"
_blue = "\033[34m"
_white = "\033[37m"
_yellow = "\033[33m"
_green = "\033[32m"
_cyan = "\033[96m"

class Color:
    """Stores 3 values representing a color with HSV codes"""
    def __init__(self, H = 0, S = 0, V = 0):
        """Initializes Color class.

        Args:
            H (int, optional): Hue. Defaults to 0.
            S (int, optional): Saturation. Defaults to 0.
            V (int, optional): Value. Defaults to 0.
        """
        assert 0 <= H <= 179, _red + f"Hue for color {repr(self)} must be bewteen 0 and 179" + _white
        assert 0 <= S <= 255, _red + f"Saturation for color {repr(self)} must be bewteen 0 and 255" + _white
        assert 0 <= V <= 255, _red + f"Value for color {repr(self)} must be bewteen 0 and 255" + _white
        self.H, self.S, self.V = H, S, V
    def AsArray(self) -> list[int]:
        """Returns the values of the color as an array.

        Returns:
            list[int]: Values H, S and V as an array.
        """
        return [self.H, self.S, self.V]
    def AsRange(self, window = 0, isLow = True) -> array:
        """Returns low or high value around acolor with range "window" as a numpy array

        Args:
            window (int, optional): Range. Defaults to 0.
            isLow (bool, optional): If true, return lowest value. Defaults to True.

        Returns:
            numpy.array: Lowest or highest array of values HSV.
        """
        assert 0 <= window <= 255, _red + f"Window range for color {repr(self)} must be bewteen 0 and 255" + _white
        if isLow: return array([self.H - window, self.S - window, self.V - window])
        else: return array([self.H + window, self.S + window, self.V + window])
    def __str__(self) -> str:
        """Representation of Color class as string

        Returns:
            str: String with HSV values
        """
        colorStr = f"Color({self.H}, {self.S}, {self.V})"
        return colorStr