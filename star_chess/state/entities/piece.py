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
    AMAZON = "amazon"
    WAMAZON = "wamazon"
    BISHOP = "bishop"
    KNIGHT = "knight"
    CAMEL = "camel"
    WILDEBEEST = "wildebeest"
    QUEEN = "queen"
    CHANCELLOR = "chancellor"
    ARCHBISHOP = "archbishop"
    GRASSHOPPER = "grasshopper"

    @classmethod
    def from_class(cls, c):
        if isinstance(King.dummy(), c):
            return cls.KING
        elif isinstance(Rook.dummy(), c):
            return cls.ROOK
        elif isinstance(Sergeant.dummy(), c):
            return cls.SERGEANT
        elif isinstance(Wamazon.dummy(), c):
            return cls.WAMAZON
        elif isinstance(Bishop.dummy(), c):
            return cls.BISHOP
        elif isinstance(Knight.dummy(), c):
            return cls.KNIGHT
        elif isinstance (Camel.dummy(), c):
            return cls.CAMEL
        elif isinstance(Wildebeest.dummy(), c):
            return cls.WILDEBEEST
        elif isinstance(Queen.dummy(), c):
            return cls.QUEEN
        elif isinstance(Chancellor.dummy(), c):
            return cls.CHANCELLOR
        elif isinstance(Archbishop.dummy(), c):
            return cls.ARCHBISHOP
        elif isinstance(Grasshopper.dummy(), c):
            return cls.GRASSHOPPER
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
            case PieceType.WAMAZON:
                return Wamazon.dummy().__class__
            case PieceType.BISHOP:
                return Bishop.dummy().__class__
            case PieceType.KNIGHT:
                return Knight.dummy().__class__
            case PieceType.CAMEL:
                return Camel.dummy().__class__
            case PieceType.WILDEBEEST:
                return Wildebeest.dummy().__class__
            case PieceType.QUEEN:
                return Queen.dummy().__class__
            case PieceType.CHANCELLOR:
                return Chancellor.dummy().__class__
            case PieceType.ARCHBISHOP:
                return Archbishop.dummy().__class__
            case PieceType.GRASSHOPPER:
                return Grasshopper.dummy().__class__
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
            case PieceType.AMAZON:
                return "A"
            case PieceType.WAMAZON:
                return "Å"
            case PieceType.BISHOP:
                return "B"
            case PieceType.KNIGHT:
                return "N"
            case PieceType.CAMEL:
                return "C"
            case PieceType.WILDEBEEST:
                return "W"
            case PieceType.QUEEN:
                return "Q"
            case PieceType.CHANCELLOR:
                return "Č"
            case PieceType.ARCHBISHOP:
                return "Ã"
            case PieceType.GRASSHOPPER:
                return "G"


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


def img_cc(color: Color) -> str:
    return "W" if color is Color.WHITE else "B"


def img_wrap(filename: str) -> str:
    return f"./img/{filename}.png"


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

    @property
    @abstractmethod
    def img_name(self) -> str:
        pass

    @property
    def img_path(self) -> str:
        return img_wrap(self.img_name)


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
    
    @property
    def img_name(self) -> str:
        return f"cr90_corvette({img_cc(self.color)})"


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

        if not ((dr == 0) ^ (dc == 0)):
            return None
        if abs(dr) == 1 or abs(dc) == 1:
            pass
        else:
            between_sta = (
                self.loc.c + (1 if dc > 0 else -1)
                if dr == 0 else
                self.loc.r + (1 if dr > 0 else -1)
            )
            between_end = (
                to.c - (1 if dc > 0 else -1)
                if dr == 0 else
                to.r - (1 if dr > 0 else -1)
            )
            rank_or_file = (
                board[to.r]
                if dr == 0 else
                [board[r][to.c] for r in range(len(board))]
            )

            if between_sta > between_end:
                between_sta, between_end = between_end, between_sta
            
            if any(
                p is not None
                for p in rank_or_file[between_sta:(between_end + 1)]
            ):
                return None

        return Move(
            self.loc,
            to,
            board[to.r][to.c] is not None
        )

    def moves(self, board: list[list[Optional[Piece]]]) -> list[Move]:
        raise NotImplementedError()
    
    @property
    def img_name(self) -> str:
        return f"e-wing_escort({img_cc(self.color)})"


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
    
    @property
    def img_name(self) -> str:
        if self.color is Color.WHITE:
            return "t-65_x-wing(W)"
        else:
            return "tie_interceptor(B)"


class Wamazon(Piece):
    color: Color
    loc: Coord
    id: int

    def can_move_to(self, board: list[list[Optional[Piece]]], to: Coord) -> Optional[Move]:
        if not (
            Rook(self.color, self.loc, None).can_move_to(board, to) or
            Bishop(self.color, self.loc, None).can_move_to(board, to) or
            Wildebeest(self.color, self.loc, None).can_move_to(board, to)
        ):
            return None
        
        return Move(
            self.loc,
            to,
            board[to.r][to.c] is not None
        )

    def moves(self, board: list[list[Optional[Piece]]]) -> list[Move]:
        raise NotImplementedError()
    
    @property
    def img_name(self) -> str:
        return f"btl-s8_k-wing({img_cc(self.color)})"


class Bishop(Piece):
    color: Color
    loc: Coord
    id: int

    def can_move_to(self, board: list[list[Optional[Piece]]], to: Coord) -> Optional[Move]:
        if not (0 <= to.r < len(board)) or not (0 <= to.c < len(board[0])):
            return None
        
        if color_at(board, to) == self.color:
            return None
        
        dist = abs(to.r - self.loc.r)

        if not (
            dist == abs(to.c - self.loc.c) and
            dist != 0
        ):
            return None

        dr = 1 if to.r > self.loc.r else -1
        dc = 1 if to.c > self.loc.c else -1

        for d in range(1, dist):
            if board[self.loc.r + dr * d][self.loc.c + dc * d] is not None:
                return None
        
        return Move(
            self.loc,
            to,
            board[to.r][to.c] is not None
        )

    def moves(self, board: list[list[Optional[Piece]]]) -> list[Move]:
        raise NotImplementedError()
    
    @property
    def img_name(self) -> str:
        return f"z-95_headhunter({img_cc(self.color)})"
    

class Knight(Piece):
    color: Color
    loc: Coord
    id: int

    def can_move_to(self, board: list[list[Optional[Piece]]], to: Coord) -> Optional[Move]:
        if not (0 <= to.r < len(board)) or not (0 <= to.c < len(board[0])):
            return None
        
        if color_at(board, to) == self.color:
            return None
        
        dr = abs(self.loc.r - to.r)
        dc = abs(self.loc.c - to.c)

        if set([dr, dc]) != {1, 2}:
            return None
        
        return Move(
            self.loc,
            to,
            board[to.r][to.c] is not None
        )

    def moves(self, board: list[list[Optional[Piece]]]) -> list[Move]:
        raise NotImplementedError()
    
    @property
    def img_name(self) -> str:
        return f"btl_y-wing({img_cc(self.color)})"


class Camel(Piece):
    color: Color
    loc: Coord
    id: int

    def can_move_to(self, board: list[list[Optional[Piece]]], to: Coord) -> Optional[Move]:
        if not (0 <= to.r < len(board)) or not (0 <= to.c < len(board[0])):
            return None
        
        if color_at(board, to) == self.color:
            return None
        
        dr = abs(self.loc.r - to.r)
        dc = abs(self.loc.c - to.c)

        if set([dr, dc]) != {1, 3}:
            return None
        
        return Move(
            self.loc,
            to,
            board[to.r][to.c] is not None
        )

    def moves(self, board: list[list[Optional[Piece]]]) -> list[Move]:
        raise NotImplementedError()
    
    @property
    def img_name(self) -> str:
        return ""


class Wildebeest(Piece):
    color: Color
    loc: Coord
    id: int

    def can_move_to(self, board: list[list[Optional[Piece]]], to: Coord) -> Optional[Move]:
        if not (
            Knight(self.color, self.loc, None).can_move_to(board, to) or
            Camel(self.color, self.loc, None).can_move_to(board, to)
        ):
            return None
        
        return Move(
            self.loc,
            to,
            board[to.r][to.c] is not None
        )

    def moves(self, board: list[list[Optional[Piece]]]) -> list[Move]:
        raise NotImplementedError()
    
    @property
    def img_name(self) -> str:
        return f"btl_y-wing({img_cc(self.color)}+)"


class Queen(Piece):
    color: Color
    loc: Coord
    id: int

    def can_move_to(self, board: list[list[Optional[Piece]]], to: Coord) -> Optional[Move]:
        if not (
            Rook(self.color, self.loc, None).can_move_to(board, to) or
            Bishop(self.color, self.loc, None).can_move_to(board, to)
        ):
            return None
        
        return Move(
            self.loc,
            to,
            board[to.r][to.c] is not None
        )

    def moves(self, board: list[list[Optional[Piece]]]) -> list[Move]:
        raise NotImplementedError()
    
    @property
    def img_name(self) -> str:
        return f"ad-1s_modular({img_cc(self.color)})"


class Chancellor(Piece):
    color: Color
    loc: Coord
    id: int

    def can_move_to(self, board: list[list[Optional[Piece]]], to: Coord) -> Optional[Move]:
        if not (
            Rook(self.color, self.loc, None).can_move_to(board, to) or
            Knight(self.color, self.loc, None).can_move_to(board, to)
        ):
            return None
        
        return Move(
            self.loc,
            to,
            board[to.r][to.c] is not None
        )

    def moves(self, board: list[list[Optional[Piece]]]) -> list[Move]:
        raise NotImplementedError()
    
    @property
    def img_name(self) -> str:
        return f"e-wing_escort({img_cc(self.color)}+)"


class Archbishop(Piece):
    color: Color
    loc: Coord
    id: int

    def can_move_to(self, board: list[list[Optional[Piece]]], to: Coord) -> Optional[Move]:
        if not (
            Bishop(self.color, self.loc, None).can_move_to(board, to) or
            Knight(self.color, self.loc, None).can_move_to(board, to)
        ):
            return None
        
        return Move(
            self.loc,
            to,
            board[to.r][to.c] is not None
        )

    def moves(self, board: list[list[Optional[Piece]]]) -> list[Move]:
        raise NotImplementedError()
    
    @property
    def img_name(self) -> str:
        return f"z-95_headhunter({img_cc(self.color)}+)"


class Grasshopper(Piece):
    color: Color
    loc: Coord
    id: int

    def can_move_to(self, board: list[list[Optional[Piece]]], to: Coord) -> Optional[Move]:
        if not (0 <= to.r < len(board)) or not (0 <= to.c < len(board[0])):
            return None
        
        if color_at(board, to) == self.color:
            return None

        def sgn(x):
            if x < 0:
                return -1
            elif x == 0:
                return 0
            else:
                return 1
        
        dr = sgn(to.r - self.loc.r)
        dc = sgn(to.c - self.loc.c)

        beforeTo = Coord(to.r - dr, to.c - dc)

        beforeMove = \
            Queen(self.color, self.loc, None).can_move_to(board, beforeTo)

        # grasshopper can also jump over pieces of the same color
        if beforeMove is None:
            beforeMove = Queen(
                Color.other(self.color), self.loc, None
            ).can_move_to(board, beforeTo)
    
        if beforeMove is None or not beforeMove.capture:
            return None
        
        return Move(
            self.loc,
            to,
            board[to.r][to.c] is not None
        )

    def moves(self, board: list[list[Optional[Piece]]]) -> list[Move]:
        raise NotImplementedError()
    
    @property
    def img_name(self) -> str:
        return f"bounty_hunter_fighter({img_cc(self.color)})"
