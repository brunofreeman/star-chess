from abc import ABC, abstractmethod
from state.color.color import Color
from state.move.move import Move

class Player(ABC):
    color: Color

    @abstractmethod
    def get_move(self) -> Move:
        pass
