from .coord import Coord
from enum import Enum
from typing import Optional
from dataclasses import dataclass


class SpecialMove(Enum):
    pass


@dataclass
class Move:
    fr: Coord
    to: Coord
    capture: bool
    special: Optional[SpecialMove] = None

    def __str__(self) -> str:
        return f"{self.fr} > {self.to} [{'x' if self.capture else ' '}]"
