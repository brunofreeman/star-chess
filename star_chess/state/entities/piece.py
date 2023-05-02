from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional
from .move.move import Move
from .move.coord import Coord
from .color.color import Color


class PieceType(Enum):
    KING = "king"
    ROOK = "rook"
    SERGEANT = "sergeant"

    @classmethod
    def from_class(cls, c):
        if isinstance(King.dummy(), c):
            return cls.KING
        elif isinstance(Rook.dummy(), c):
            return cls.ROOK
        elif isinstance(Sergeant.dummy(), c):
            return cls.SERGEANT
        else:
            raise ValueError()
    
    def to_class(self):
        match self:
            case PieceType.KING:
                return King.dummy().__class__
            case PieceType.ROOK:
                return Rook.dummy().__class__
            case PieceType.SERGEANT:
                return Sergeant.dummy().__class__
        raise ValueError()
    
    @property
    def char_code(self) -> str:
        match self:
            case PieceType.KING:
                return "K"
            case PieceType.ROOK:
                return "R"
            case PieceType.SERGEANT:
                return "S"


def new_piece(type: PieceType, color: Color, loc: Coord, _id: list[int] = [0]) -> Piece:
    piece = type.to_class()(color, loc, _id[0])
    _id[0] += 1
    return piece


def color_at(board: list[list[Optional[Piece]]], r: int | Coord, c: Optional[int] = None) -> Optional[Color]:
    if isinstance(r, Coord):
        r, c = r.r, r.c

    if board[r][c] is None:
        return None
    else:
        return board[r][c].color


class Piece(ABC):
    color: Color
    loc: Coord
    id: int

    def __init__(self, color: Color, loc: Coord, id: int):
        self.color = color
        self.loc = loc
        self.id = id

    @classmethod
    def dummy(cls):
        return cls(Color.WHITE, Coord(0, 0), -1)

    @property
    def type(self):
        return PieceType.from_class(self.dummy().__class__)
    
    @abstractmethod
    def can_move_to(self, board: list[list[Optional[Piece]]], to: Coord) -> Optional[Move]:
        pass

    @abstractmethod
    def moves(self, board: list[list[Optional[Piece]]]) -> list[Move]:
        pass


class King(Piece):
    color: Color
    loc: Coord
    id: int

    def can_move_to(self, board: list[list[Optional[Piece]]], to: Coord) -> Optional[Move]:
        if not (0 <= to.r < len(board)) or not (0 <= to.c < len(board[0])):
            return None
        
        if color_at(board, to) == self.color:
            return None

        dr = to.r - self.loc.r
        dc = to.c - self.loc.c
        
        if abs(dr) > 1 or abs(dc) > 1 or (abs(dr) == abs(dc) == 0):
            return None
        
        return Move(
            self.loc,
            to,
            board[to.r][to.c] is not None
        )
        
    def moves(self, board: list[list[Optional[Piece]]]) -> list[Move]:
        mvs = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == dc == 0:
                    continue
                r = self.loc.r + dr
                c = self.loc.c + dc
                if not (0 <= r < len(board)):
                    continue
                if not (0 <= c < len(board[0])):
                    continue
                if board[r][c] is not None and board[r][c].color == self.color:
                    continue
                mvs.append(Move(
                    self.loc,
                    Coord(r, c),
                    board[r][c] is not None
                ))
        return mvs


class Rook(Piece):
    color: Color
    loc: Coord
    id: int

    def can_move_to(self, board: list[list[Optional[Piece]]], to: Coord) -> Optional[Move]:
        if not (0 <= to.r < len(board)) or not (0 <= to.c < len(board[0])):
            return None
        
        if color_at(board, to) == self.color:
            return None
        
        dr = to.r - self.loc.r
        dc = to.c - self.loc.c

        if dr == dc == 0 or not (dr == 0 or dc == 0):
            return None
        elif dr == 0:
            between_sta = self.loc.c + (1 if dc > 0 else -1)
            between_end = to.c - (1 if dc > 0 else -1)

            if between_sta > between_end:
                between_sta, between_end = between_end, between_sta
            
            if any(p is not None for p in board[to.r][between_sta:(between_end + 1)]):
                return None
        elif dc == 0:
            between_sta = self.loc.r + (1 if dr > 0 else -1)
            between_end = to.r - (1 if dr > 0 else -1)
            if between_sta > between_end:
                between_sta, between_end = between_end, between_sta

            col = [board[r][to.c] for r in range(len(board))]
            
            if any(p is not None for p in col[between_sta:(between_end + 1)]):
                return None

        return Move(
            self.loc,
            to,
            board[to.r][to.c] is not None
        )

    def moves(self, board: list[list[Optional[Piece]]]) -> list[Move]:
        raise NotImplementedError()


class Sergeant(Piece):
    color: Color
    loc: Coord
    id: int

    def can_move_to(self, board: list[list[Optional[Piece]]], to: Coord) -> Optional[Move]:
        if not (0 <= to.r < len(board)) or not (0 <= to.c < len(board[0])):
            return None
        
        if color_at(board, to) == self.color:
            return None
        
        dir = 1 if self.color is Color.WHITE else -1

        if to.r != self.loc.r + dir:
            return None
        
        if (abs(to.c - self.loc.c) > 1):
            return None
        
        return Move(
            self.loc,
            to,
            board[to.r][to.c] is not None
        )

    def moves(self, board: list[list[Optional[Piece]]]) -> list[Move]:
        raise NotImplementedError()
