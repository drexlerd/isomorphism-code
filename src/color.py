
from typing import MutableSet

class Color:
    """ A color is just an integer with attached meaning for interpretation.
    """
    def __init__(self, value: int, labels: MutableSet[str], info: str = ""):
        """
        Args:
            value: the color representation as integer value
            labels: the color representation as strings
            info: additional information for visualization
        """
        self._value = value
        self._labels = labels
        self._info = info

    def __eq__(self, other : "Color"):
        return self._value == other._value

    def __hash__(self):
        return hash(self._value)
    
    def __str__(self):
        """ Create a string representation with optional info.
        """
        labels = "{" + ", ".join(self._labels) + "}"
        representation = f"{self._value}={labels}"
        if self._info:
            representation += f" ({self._info})"
        return representation

    @property 
    def value(self):
        return self._value
    
    @property
    def labels(self):
        return self._labels
    
    @property
    def info(self):
        return self._info
    