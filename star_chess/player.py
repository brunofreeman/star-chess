from abc import ABC, abstractmethod
from typing import Optional
from frontend import FrontendFancyGUI
from network import MOVE_PASS, MOVE_FORFEIT, server_clear, server_submit, \
    server_submit_special, server_query, server_save
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
    def game_begin(self):
        pass

    @abstractmethod
    def game_end(self, state: State):
        pass

    @abstractmethod
    def round_begin(self):
        pass

    @abstractmethod
    def round_end(self):
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

    def game_begin(self):
        print("It's time to do battle, captain!")
        print("Input ship maneuvers using \"from > to\" format.")
        print("Specify \"from\" and \"to\" in standard chess notation.")

    def round_begin(self):
        pass

    def game_end(self, state: State):
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

    def game_begin(self):
        self.illegal(self.game_begin)

    def game_end(self, state: State):
        self.illegal(self.game_end)

    def round_begin(self):
        self.illegal(self.round_begin)

    def round_end(self):
        self.illegal(self.round_end)
    
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

    def game_begin(self):
        print("It's time to do battle, captain!")
        print("Click to select which ship to move.")
        print("Shift-click to select where to move.")
        print("Press [enter] in the terminal to submit move.")
        print("Illegal moves will be rejected and counted as a pass.")

    def game_end(self, state: State):
        if state.winner == self.color:
            print("Well fought, captain!")
        else:
            print("Retreat for now, captain!")

    def round_begin(self):
        pass

    def round_end(self):
        pass


class PlayerOnlineFancyGUI(Player):
    color: Color
    frontend: FrontendFancyGUI
    uname: str
    uname_opponent: str

    def __init__(
            self, color: Color, frontend: FrontendFancyGUI,
            username: Optional[str] = None, opponent: Optional[str] = None):
        self.color = color
        self.frontend = frontend
        self.uname = self.color.name if username is None else username
        self.uname_opponent = \
            Color.other(self.color).name if opponent is None else opponent
        server_clear(self.uname)
    
    def get_move(self, state: State) -> tuple[Optional[Move], bool]:
        while True:
            fr = None
            to = None
            attempted_cmd = False
            test_move = False
            cmd = ""
            msg = None
            

            while fr is None or to is None:
                test_move = False

                cmd = input(f"[{state.turn_no:>3d}] ")

                attempted_cmd = cmd != ""

                if cmd in [":exit", ":quit"]:
                    server_submit_special(
                        self.uname, MOVE_FORFEIT, state.turn_no)
                    return None, True
                elif cmd == ":pass":
                    server_submit_special(
                        self.uname, MOVE_PASS, state.turn_no)
                    return None, False
                elif cmd == ":test":
                    test_move = True
                elif cmd.startswith(":chat "):
                    newMsg = cmd[len(":chat "):]
                    print(f"The message\n'''\n{newMsg}\n'''\nwill broadcast " +
                           "to enemy vessels when you make your next manuever.")
                    if msg is not None:
                        print("Your previous message has been overwritten.")
                    msg = newMsg
                    continue

                fr = self.frontend.move_fr
                to = self.frontend.move_to

                if attempted_cmd:
                    print(f"Command '{cmd}' not recognized!")
            
            moving = state.board.piece_at(fr)
            move = None if moving is None else moving.can_move_to(
                state.board.board, to)
            if move is not None:
                move.msg = msg

            if moving is None:
                print("There is no ship there to command!")
            elif moving.color is not self.color:
                print("You cannot command an enemy vessel!")
            elif move is None:
                print("That ship cannot perform that manuever!")
            elif state.board.exists_check_after_move(self.color, move):
                print("That manuever would leave your primary vessel under attack!")
            elif test_move:
                print("That's a valid manuever, captain!")
            else:
                if state.board.exists_check_after_move(
                    Color.other(self.color), move
                ):
                    print("You've put the enemy's primary vessel under attack!")
                server_submit(self.uname, move, state.turn_no)
                return move, False

    def play_again(self) -> bool:
        return False
    
    def rematch_rejected(self):
        pass

    def game_begin(self):
        print("It's time to do battle, captain!")
        print("Click to select which ship to move.")
        print("Shift-click to select where to move.")
        print("Press [enter] in the terminal to submit the move.")

    def game_end(self, state: State):
        if state.winner == self.color:
            print("Well fought, captain!")
        else:
            print("Retreat for now, captain!")

    def round_begin(self):
        pass

    def round_end(self):
        server_save(self.uname)


class PlayerOnlineOpponent(Player):
    color: Color
    username: str

    def __init__(self, color: Color, username: Optional[str] = None):
        self.color = color
        self.username = self.color.name if username is None else username

    def get_move(self, state: State) -> tuple[Optional[Move], bool]:
        print(f"[{state.turn_no:>3d}] Waiting for opponent's move...")
        move, resign = server_query(self.username, state.turn_no)
        if (
            move is not None and
            state.board.exists_check_after_move(Color.other(self.color), move)
        ):
            print("Your primary vessel is under attack, captain!")
            print("You must perform evasive manuevers!")
        if move is not None and move.msg is not None:
            print("Enemy transmission received:")
            print(f">>> {move.msg}")
        return move, resign

            
    def play_again(self) -> bool:
        return False
    
    def rematch_rejected(self):
        self.illegal(self.rematch_rejected)

    def game_begin(self):
        self.illegal(self.game_begin)

    def game_end(self, state: State):
        self.illegal(self.game_end)

    def round_begin(self):
        self.illegal(self.round_begin)

    def round_end(self):
        self.illegal(self.round_end)
    
    def illegal(self, func):
        raise Exception(f"{self.__class__}:{func} should not be called")
