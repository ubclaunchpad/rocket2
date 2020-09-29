"""Data model to represent permissions."""
from enum import Enum


class OrderedEnum(Enum):
    """
    Comparable enum -
    copied from https://docs.python.org/3/library/enum.html#orderedenum
    """

    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self.value >= other.value
        return NotImplemented

    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented

    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self.value <= other.value
        return NotImplemented

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented


class Permissions(OrderedEnum):
    """Enum to represent possible permissions levels."""

    member = 1
    team_lead = 2
    admin = 3

    def __str__(self) -> str:
        """Return the string without 'Permissions.' prepended."""
        return self.name
