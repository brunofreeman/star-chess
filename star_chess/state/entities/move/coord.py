from dataclasses import dataclass


@dataclass
class Coord:
    c: int
    r: int

    @classmethod
    def from_str(cls, s):
        return cls(
            ord(s[0]) - ord('a'),
            int(s[1:]) - 1
        )

    def __str__(self):
        return f"{chr(self.c + 'a')}{self.r + 1}"  
