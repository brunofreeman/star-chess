from abc import ABC, abstractmethod
import board as b
from move.move import Move
from color.color import Color

class Piece(ABC):
    board: b.Board
    id: int
    color: Color

    @abstractmethod
    def moves() -> set[Move]:
        pass
