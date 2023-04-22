from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional
from move.move import Move
from move.coord import Coord
from color.color import Color


class PieceType(Enum):
    KING = "king"
    ROOK = "rook"
    SERGEANT = "sergeant"

    @classmethod
    def from_class(cls, c):
        match c:
            case King.__class__:
                return cls.KING
            case Rook.__class__:
                return cls.ROOK
            case Sergeant.__class__:
                return cls.SERGEANT
    
    def to_class(self):
        match self:
            case PieceType.KING:
                return King.__class__
            case PieceType.ROOK:
                return Rook.__class__
            case PieceType.SERGEANT:
                return Sergeant.__class__


_id: int = 0
def new_piece(type: PieceType, color: Color, loc: Coord) -> Piece:
    piece = type.to_class(color, loc. _id)
    _id += 1
    return piece


class Piece(ABC):
    color: Color
    loc: Coord
    id: int

    def __init__(self, color: Color, loc: Coord, id: int):
        self.color = color
        self.loc = loc
        self.id = id

    @abstractmethod
    def moves(self, board: list[list[Optional[Piece]]]) -> set[Move]:
        pass


class King(Piece):
    color: Color
    loc: Coord
    id: int

    def moves(self, board: list[list[Optional[Piece]]]) -> set[Move]:
        raise NotImplementedError()


class Rook(Piece):
    color: Color
    loc: Coord
    id: int

    def moves(self, board: list[list[Optional[Piece]]]) -> set[Move]:
        raise NotImplementedError()


class Sergeant(Piece):
    color: Color
    loc: Coord
    id: int

    def moves(self, board: list[list[Optional[Piece]]]) -> set[Move]:
        raise NotImplementedError()
