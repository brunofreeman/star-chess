from abc import ABC, abstractmethod
from typing import Optional
from frontend import FrontendFancyGUI
from network import MOVE_PASS, MOVE_FORFEIT, server_clear, server_submit, \
    server_submit_special, server_query, server_save
from state.entities.color.color import Color
from state.entities.move.move import Move, SpecialMove
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
    used_hyperdrive: bool

    def __init__(
            self, color: Color, frontend: FrontendFancyGUI,
            username: Optional[str] = None, opponent: Optional[str] = None):
        self.color = color
        self.frontend = frontend
        self.uname = self.color.name if username is None else username
        self.uname_opponent = \
            Color.other(self.color).name if opponent is None else opponent
        self.used_hyperdrive = False
    
    def get_move(self, state: State) -> tuple[Optional[Move], bool]:
        if state.board.is_checkmated(self.color):
            print("There's no escape! You've been checkmated!")
            server_submit_special(
                self.uname, MOVE_FORFEIT, state.turn_no)
            return None, True
        
        msg = None

        while True:
            fr = None
            to = None
            attempted_cmd = False
            test_move = False
            hyperdrive = False
            cmd = ""
            

            while fr is None or to is None:
                test_move = False
                hyperdrive = False

                cmd = input(f"[{state.turn_no:>3d}] ")

                attempted_cmd = cmd != ""

                if cmd in [":exit", ":quit"]:
                    server_submit_special(
                        self.uname, MOVE_FORFEIT, state.turn_no)
                    return None, True
                elif cmd == ":pass":
                    if state.board.exists_check(self.color):
                        print("Now's no time to freeze up captain! "+
                              "We're in their crosshairs!")
                        server_submit_special(
                            self.uname, MOVE_FORFEIT, state.turn_no)
                        return None, True
                    else:
                        print("Thanks for being honest, captain :)")
                        server_submit_special(
                            self.uname, MOVE_PASS, state.turn_no)
                        return None, False
                elif cmd == ":test":
                    test_move = True
                elif cmd.startswith(":chat "):
                    newMsg = cmd[len(":chat "):]
                    print(f"The message\n'''\n{newMsg}\n'''\nwill broadcast " +
                           "to enemy vessels when you make your next maneuver.")
                    if msg is not None:
                        print("Your previous message has been overwritten.")
                    msg = newMsg
                    continue
                elif cmd == ":hyperdrive":
                    if self.used_hyperdrive:
                        print("No can do, captain! The corvette can only use hyperdrive once!")
                        continue
                    else:
                        hyperdrive = True
                elif attempted_cmd:
                    print(f"Command '{cmd}' not recognized!")
                    continue

                fr = self.frontend.move_fr
                to = self.frontend.move_to

            moving = state.board.piece_at(fr)
            move = None if moving is None else moving.can_move_to(
                state.board.board, to,
                SpecialMove.HYPERDRIVE if hyperdrive else None)
            if move is not None:
                move.msg = msg

            if moving is None:
                print("There is no ship there to command!")
            elif moving.color is not self.color:
                print("You cannot command an enemy vessel!")
            elif test_move:
                if move is None:
                    print("That ship cannot perform that maneuver!")
                else:
                    print("That's a valid maneuver, captain!")
            elif not test_move and move is None:
                if state.board.exists_check(self.color):
                    print("That maneuver cannot be made! Defend your corvette!")
                else:
                    print("Not possible, captain! We don't have time for " +
                        "commands that can't be followed!")
                    server_submit_special(
                        self.uname, MOVE_PASS, state.turn_no)
                    return None, False
            elif state.board.exists_check_after_move(self.color, move):
                print("That maneuver would leave your corvette under attack!")
            else:
                if state.board.exists_check_after_move(
                    Color.other(self.color), move
                ):
                    print("You've put the enemy's corvette under attack!")
                if hyperdrive:
                    self.used_hyperdrive = True
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
            print("Well fought, captain! You won the battle!")
        else:
            print("Retreat for now, captain! Better luck next time!")
        input("Press [enter] to exit. " +
              "And then ask your alumni if you have time to play again!")

    def round_begin(self):
        self.used_hyperdrive = False
        if self.color is Color.WHITE:
            server_clear(self.uname)
            server_clear(self.uname_opponent)


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
            print("Your corvette vessel is under attack, captain!")
            print("You must perform evasive maneuvers!")
        if move is not None and move.msg is not None:
            print("Enemy transmission received:")
            print(f">>> {move.msg}")
        if move is None and not resign:
            print("The enemy is faltering! Now's your chance!")
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
