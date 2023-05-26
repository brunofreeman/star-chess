from .coord import Coord
from enum import Enum
from typing import Optional
from dataclasses import dataclass


class SpecialMove(Enum):
    HYPERDRIVE = 0


@dataclass
class Move:
    fr: Coord
    to: Coord
    capture: bool
    special: Optional[SpecialMove] = None
    msg: Optional[str] = None

    def __str__(self) -> str:
        return f"{self.fr} > {self.to} [{'x' if self.capture else ' '}]"
