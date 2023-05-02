from random import randint
from enum import Enum


class Color(Enum):
    WHITE = 0
    BLACK = 1

    @classmethod
    def other(cls, color):
        return cls.WHITE if color is cls.BLACK else cls.BLACK
    
    @classmethod
    def random(cls):
        return cls(randint(0, 1))
