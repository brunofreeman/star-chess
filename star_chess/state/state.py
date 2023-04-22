from entities.board import Board
from .entities.color.color import Color
from .entities.move.move import Move


class State:
    spec: str
    board: Board
    pov: Color
    has_turn: Color
    turn: int

    def __init__(self, spec: str, color: Color):
        self.spec = spec
        self.pov = color
        self.reset()
    
    def reset(self):
        self.board = Board(self.spec)
        self.has_turn = Color.White
        self.turn = 0

    def make_move(self, move: Move):
        pass

    def resign_player(self, color: Color):
        pass
    
    def pass_turn(self):
        self.has_turn = Color.other(self.has_turn)
        self.turn += 1
    
    def is_game_over(self) -> bool:
        pass
