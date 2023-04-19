from coord import Coord
from enum import Enum
from typing import Optional

class SpecialMove(Enum):
    pass

class Move:
    fr: Coord
    to: Coord
    capture: bool
    special: Optional[SpecialMove]
    