from abc import ABC, abstractmethod
from typing import Optional
from frontend import FrontendFancyGUI
from network import MOVE_PASS, MOVE_FORFEIT, server_clear, server_submit, \
    server_submit_special, server_query
from state.entities.color.color import Color
from state.entities.move.move import Move
from state.entities.move.coord import Coord
from state.state import State


class Player(ABC):
    color: Color

    @abstractmethod
    def get_move(self, state: State) -> tuple[Optional[Move], bool]:
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

    def __init__(self, color: Color):
        self.color = color

    def get_move(self, state: State) -> tuple[Optional[Move], bool]:
        while True:
            move_str = input("$ ")
            move_str = "".join([c for c in move_str if c != ' '])

            if move_str in ["quit", "exit", "forfeit", "concede"]:
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
    tenacity: float

    def __init__(self, color: Color, tenacity: float = 3.0):
        self.color = color
        self.tenacity = tenacity

    def get_move(self, state: State) -> tuple[Optional[Move], bool]:
        input("# press [enter] for AI move")
        
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


class PlayerFancyGUI(Player):
    color: Color
    frontend: FrontendFancyGUI

    def __init__(self, color: Color, frontend: FrontendFancyGUI):
        self.color = color
        self.frontend = frontend

    def get_move(self, state: State) -> tuple[Optional[Move], bool]:
        fr = None
        to = None

        while fr is None or to is None:
            cmd = input("$ ")

            if cmd in ["quit", "exit", "forfeit", "concede"]:
                return None, True

            fr = self.frontend.move_fr
            to = self.frontend.move_to
        
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
        print("Click to select which ship to move.")
        print("Shift-click to select where to move.")
        print("Press [enter] in the terminal to submit move.")
        print("Illegal moves will be rejected and counted as a pass.")

    def msg_round(self):
        pass

    def msg_end(self, state: State):
        if state.winner == self.color:
            print("Well fought, captain!")
        else:
            print("Retreat for now, captain!")


class PlayerOnlineFancyGUI(Player):
    color: Color
    frontend: FrontendFancyGUI

    def __init__(self, color: Color, frontend: FrontendFancyGUI):
        self.color = color
        self.frontend = frontend
        server_clear(self.username)
    
    @property
    def username(self) -> str:
        return self.color.name
    
    @property
    def usernameOpponent(self) -> str:
        return Color.other(self.color).name

    def get_move(self, state: State) -> tuple[Optional[Move], bool]:
        while True:
            fr = None
            to = None

            while fr is None or to is None:
                cmd = input(f"[{state.turn_no:>3d}] ")

                if cmd in ["quit", "exit", "forfeit", "concede"]:
                    server_submit_special(self.username, MOVE_FORFEIT, state.turn_no)
                    return None, True

                fr = self.frontend.move_fr
                to = self.frontend.move_to
            
            moving = state.board.piece_at(fr)

            if moving is None:
                print("There is no ship there to command!")
            elif moving.color is not self.color:
                print("You cannot command an enemy vessel!")
            else:
                move = moving.can_move_to(state.board.board, to)
                if move is None:
                    print("That ship cannot perform that manuever!")
                else:
                    server_submit(self.username, move, state.turn_no)
                    return move, False

    def play_again(self) -> bool:
        return False
    
    def rematch_rejected(self):
        pass

    def msg_init(self):
        print("It's time to do battle, captain!")
        print("Click to select which ship to move.")
        print("Shift-click to select where to move.")
        print("Press [enter] in the terminal to submit the move.")

    def msg_round(self):
        pass

    def msg_end(self, state: State):
        if state.winner == self.color:
            print("Well fought, captain!")
        else:
            print("Retreat for now, captain!")


class PlayerOnlineOpponent(Player):
    color: Color

    def __init__(self, color: Color):
        self.color = color
    
    @property
    def username(self) -> str:
        return self.color.name

    def get_move(self, state: State) -> tuple[Optional[Move], bool]:
        print(f"[{state.turn_no:>3d}] Waiting for opponent's move...")
        return server_query(self.username, state.turn_no)
            
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
