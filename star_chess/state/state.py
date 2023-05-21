from typing import Optional
from .entities.board import Board
from .entities.color.color import Color
from .entities.move.move import Move
from .entities.piece import King


class State:
    spec: str
    board: Board
    pov: Color
    has_turn: Color
    turn_no: int
    winner: Optional[Color]

    def __init__(self, spec: str, color: Color):
        self.spec = spec
        self.pov = color
        self.reset()
    
    def reset(self):
        self.board = Board(self.spec)
        self.has_turn = Color.WHITE
        self.turn_no = 0
        self.winner = None

    # trusts that given move is a valid one to make
    def make_move(self, move: Move):
        if isinstance(self.board.piece_at(move.to), King):
            self.winner = self.has_turn
        self.board.move_piece(move.fr, move.to)
        self.pass_turn()

    def resign_player(self, color: Color):
        self.winner = Color.other(color)
    
    def pass_turn(self):
        self.has_turn = Color.other(self.has_turn)
        self.turn_no += 1
    
    def is_game_over(self) -> bool:
        return self.winner is not None
