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

    def __str__(self):
        return f"{chr(self.c + 'a')}{self.r + 1}"  
