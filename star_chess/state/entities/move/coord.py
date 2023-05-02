from random import randint
from dataclasses import dataclass


@dataclass
class Coord:
    r: int
    c: int

    @classmethod
    def from_str(cls, s):
        return cls(
            int(s[1:]) - 1,
            ord(s[0]) - ord('a')
        )
    
    @classmethod
    def random(cls, n_rows, n_cols):
        return cls(
            randint(0, n_rows - 1),
            randint(0, n_cols - 1)
        )

    def __str__(self) -> str:
        return f"{chr(self.c + ord('a'))}{self.r + 1}"
    
    def __iter__(self):
        return (x for x in (self.r, self.c))
    
    def __eq__(self, other) -> bool:
        return self.r == other.r and self.c == other.c
    
    def __hash__(self) -> int:
        return hash(self.__str__())
