from abc import ABC, abstractmethod
from color import Color
from move import Move

class Player(ABC):
    color: Color

    @abstractmethod
    def get_move(self) -> Move:
        pass