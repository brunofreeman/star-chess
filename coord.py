from dataclasses import dataclass

@dataclass
class Coord:
    c: int
    r: int

    def __str__(self):
        return f"{chr(self.c + 'a')}{self.r + 1}"  
