import json
# from tabulate import tabulate
from typing import Optional, Tuple
from .piece import *
from .color.color import Color
from .move.coord import Coord


class Board:
    # white promotes at highest-index row, black at row 0
    board: list[list[Optional[Piece]]]
    map: dict[Tuple[Color, PieceType], set[Coord]]

    def __init__(self, spec_path: str):
        if not spec_path.endswith(".json"):
            raise ValueError()

        with open(spec_path) as spec_file:
            spec = json.loads(spec_file.read())

        assert {"size", "white", "black"} == set(spec.keys())

        size, white, black = spec["size"], spec["white"], spec["black"]

        assert PieceType.KING.value in white and PieceType.KING.value in black

        self.board = [[None for _ in range(size["w"])] for _ in range(size["h"])]
        self.map = dict()

        self.add_piece(
            PieceType.KING,
            Color.WHITE,
            Coord.from_str(white[PieceType.KING.value])
        )
        self.add_piece(
            PieceType.KING,
            Color.BLACK,
            Coord.from_str(black[PieceType.KING.value])
        )

        for color, dct in [(Color.WHITE, white), (Color.BLACK, black)]:
            for name, locs in [(n, ls) for (n, ls) in dct.items() if n != PieceType.KING.value]:
                for loc in locs:
                    self.add_piece(
                        PieceType(name),
                        color,
                        Coord.from_str(loc)
                    )
    
    def piece_at(self, x: Coord | int, c: Optional[int] = None) -> Optional[Piece]:
        if isinstance(x, Coord):
            return self.board[x.r][x.c]
        else:
            return self.board[x][c]

    def _map_add(self, c: Coord):
        p = self.piece_at(c)

        if p is None:
            return
        
        key = (p.color, p.type)

        if key not in self.map:
            self.map[key] = set()

        self.map[key].add(c)

    def _map_remove(self, p: Piece, c: Coord):
        key = (p.color, p.type)

        self.map[key].remove(c)

        if len(self.map[key]) == 0:
            del self.map[key]
    
    def add_piece(self, type: PieceType, color: Color, coord: Coord):
        assert self.board[coord.r][coord.c] is None
        self.board[coord.r][coord.c] = new_piece(type, color, coord)
        self._map_add(coord)
    
    def remove_piece(self, coord: Coord) -> Optional[Piece]:
        piece = self.piece_at(coord)
        if piece is None:
            return
        self._map_remove(piece, coord)
        self.board[coord.r][coord.c] = None
        return piece

    def move_piece(self, fr: Coord, to: Coord):
        assert self.board[fr.r][fr.c] is not None
        # remove captured piece, if any
        self.remove_piece(to)
        # remove moving piece from old location
        moving = self.remove_piece(fr)
        # insert moving piece at new location
        self.add_piece(moving.type, moving.color, to)
    
    @property
    def n_rows(self) -> int:
        return len(self.board)
    
    @property
    def n_cols(self) -> int:
        return len(self.board[0])

    def n_squares(self) -> int:
        return self.n_rows * self.n_cols
    
    def exists_check(self, color: Color) -> bool:
        king = None

        for r in range(self.n_rows):
            for c in range(self.n_cols):
                p = self.piece_at(r, c)
                if isinstance(p, King) and p.color is color:
                    king = p
                    break
            else:
                continue
            break
        
        if king is None:
            raise ValueError(self.board)
        
        return any(
            any(
                self.piece_at(r, c) is not None and
                self.piece_at(r, c).can_move_to(
                    self.board, king.loc
                )
                for c in range(self.n_cols)
            )
            for r in range(self.n_rows)
        )

    def exists_check_after_move(self, color: Color, move: Move) -> bool:
        restore = self.piece_at(move.to)

        self.move_piece(move.fr, move.to)
        
        check_exists = self.exists_check(color)

        self.move_piece(move.to, move.fr)

        if restore is not None:
            self.add_piece(restore.type, restore.color, restore.loc)
        
        return check_exists
        
    def __str__(self) -> str:
        # char_codes = [
        #     [
        #         " " if p is None else
        #         (p.type.char_code if p.color == Color.WHITE else p.type.char_code.lower())
        #         for p in row
        #     ]
        #     for row in self.board
        # ]
        # char_codes.reverse() # put row 0 at bottom of display

        # with_labels = [
        #     [str(len(self.board) - i), *char_codes[i]]
        #     for i in range(len(self.board))
        # ]
        # with_labels.append(
        #     [" ", *[chr(ord('a') + i) for i in range(len(self.board[0]))]]
        # )
        
        # return tabulate(with_labels, tablefmt="fancy_grid")

        return "__str__ disabled to reduce dependencies"
