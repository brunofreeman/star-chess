from enum import Enum


class Color(Enum):
    White = 0
    Black = 1

    @classmethod
    def other(cls, color):
        return cls.White if color is cls.Black else cls.Black
