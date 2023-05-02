import time
from abc import ABC, abstractmethod
from typing import Optional, Tuple
from frontend import Frontend
from state.entities.color.color import Color
from state.entities.move.move import Move
from state.entities.move.coord import Coord
from state.state import State


class Player(ABC):
    color: Color
    sec_per_move: Optional[float]
    frontend: Optional[Frontend]

    @abstractmethod
    def get_move(self, state: State) -> Tuple[Optional[Move], bool]:
        pass

    @abstractmethod
    def play_again(self) -> bool:
        pass
    
    @abstractmethod
    def rematch_rejected(self):
        pass
    
    @abstractmethod
    def msg_init(self):
        pass

    @abstractmethod
    def msg_round(self):
        pass

    @abstractmethod
    def msg_end(self, state: State):
        pass


class PlayerCLI(Player):
    color: Color
    sec_per_move: Optional[float]
    frontend: Optional[Frontend]

    def __init__(self, color: Color):
        self.color = color
        self.sec_per_move = None
        self.frontend = None

    def get_move(self, state: State) -> Tuple[Optional[Move], bool]:
        while True:
            move_str = input("$ ")
            move_str = "".join([c for c in move_str if c != ' '])

            if move_str in ["self-destruct", "quit", "exit"]:
                return None, True
            
            coord_strs = move_str.split('>')
            if len(coord_strs) != 2:
                continue

            try:
                fr = Coord.from_str(coord_strs[0])
                to = Coord.from_str(coord_strs[1])
                break
            except:
                continue
        
        moving = state.board.piece_at(fr)

        if moving is None:
            return None, False
        else:
            return moving.can_move_to(state.board.board, to), False

    def play_again(self) -> bool:
        return False
    
    def rematch_rejected(self):
        pass

    def msg_init(self):
        print("It's time to do battle, captain!")
        print("Input ship maneuvers using \"from > to\" format.")
        print("Specify \"from\" and \"to\" in standard chess notation.")

    def msg_round(self):
        pass

    def msg_end(self, state: State):
        if state.winner == self.color:
            print("Well fought, captain!")
        else:
            print("Retreat for now, captain!")


class PlayerRandomAI(Player):
    color: Color
    sec_per_move: Optional[float]
    frontend: Optional[Frontend]
    tenacity: float

    def __init__(self, color: Color, tenacity: float = 3.0):
        self.color = color
        self.sec_per_move = None
        self.frontend = None
        self.tenacity = tenacity

    def get_move(self, state: State) -> Tuple[Optional[Move], bool]:
        time.sleep(2)
        
        n = int(state.board.n_squares() * self.tenacity)

        for _ in range(n):
            fr = Coord.random(state.board.n_rows(), state.board.n_cols())
            to = Coord.random(state.board.n_rows(), state.board.n_cols())

            moving = state.board.piece_at(fr)

            if moving is None or moving.color != self.color:
                continue

            move = moving.can_move_to(state.board.board, to)

            if move is None:
                continue
            else:
                print(f"# {move} played by opponent")
                return move, False

        print("# opponent passed the turn")
        return None, False

    def play_again(self) -> bool:
        return False
    
    def rematch_rejected(self):
        self.illegal(self.rematch_rejected)

    def msg_init(self):
        self.illegal(self.msg_init)

    def msg_round(self):
        self.illegal(self.msg_round)

    def msg_end(self, state: State):
        self.illegal(self.msg_end)
    
    def illegal(self, func):
        raise Exception(f"{self.__class__}:{func} should not be called")
