from abc import ABC, abstractmethod
from typing import Optional, Tuple
from frontend import Frontend
from state.color.color import Color
from state.move.move import Move
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
