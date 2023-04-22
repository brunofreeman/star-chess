import json
from typing import Optional, Tuple
from .piece import *
from .color.color import Color
from .move.coord import Coord


class Board:
    board: list[list[Optional[Piece]]]
    map: dict[Tuple[PieceType, Color], Coord] # TODO

    def __init__(self, spec_path: str):
        assert spec_path.endswith(".json")

        with open(spec_path) as spec_file:
            spec = json.loads(spec_file.read())

        assert {"size", "white", "black"} == set(spec.keys())

        size, white, black = spec["size"], spec["white"], spec["black"]

        assert PieceType.KING.value in white and PieceType.KING.value in black

        self.board = [[None] * size["w"]] * size["h"]

        self.add_piece(
            PieceType.KING,
            Color.White,
            Coord.from_str(white[PieceType.KING.value])
        )
        self.add_piece(
            PieceType.KING,
            Color.Black,
            Coord.from_str(black[PieceType.KING.value])
        )

        for color, dict in [(Color.White, white), (Color.Black, black)]:
            for name, locs in [(n, ls) for (n, ls) in dict.items() if n != PieceType.KING.value]:
                for loc in locs:
                    self.add_piece(
                        PieceType(name),
                        color,
                        Coord.from_str(loc)
                    )
    
    def add_piece(self, type: PieceType, color: Color, coord: Coord):
        piece = new_piece(type, color, coord)
        self.board[coord.r][coord.c] = piece
    
    # def coords_king(self, color: Color) -> Coord:
    #     for piece in [p for ps in self.board for p in ps]:
    #         if piece.color == color and isinstance(piece, King):
    #             return piece.loc
