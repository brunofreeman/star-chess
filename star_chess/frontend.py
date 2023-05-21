from abc import ABC, abstractmethod
from typing import Optional
import tkinter as tk
from PIL import ImageTk, Image
from state.state import State
from state.entities.color.color import Color
from state.entities.move.coord import Coord


class Frontend(ABC):
    @abstractmethod
    def display_init(self, state: State):
        pass

    @abstractmethod
    def display_update(self, state: State, changed: Optional[set[Coord]]):
        pass

    @abstractmethod
    def display_end(self):
        pass


class FrontendTextGUI(Frontend):
    root: tk.Tk
    ascii_board: tk.Text

    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("800x800")
        self.root.aspect(1, 1, 1, 1)
        self.root.title("Star Chess")

        self.ascii_board = tk.Text(
            self.root,
            font=("Courier New", 12),
            state=tk.DISABLED
        )

    def display_init(self, state: State):
        self.display_update(state)
        self.ascii_board.pack()

    def display_update(self, state: State, changed: Optional[set[Coord]]):
        self.ascii_board.configure(state=tk.NORMAL)
        self.ascii_board.delete(1.0, tk.END)
        self.ascii_board.insert(tk.END, str(state.board))
        self.ascii_board.update()
        self.ascii_board.configure(state=tk.DISABLED)

    def display_end(self):
        self.root.quit()
        self.root.destroy()


class FrontendFancyGUI(Frontend):
    window_dim: tuple[int, int] = (800, 800)

    cell_padding: int = 0
    cell_weight: int = 1

    hex_codes: dict[Color, tuple[str, str]] = {
        # (default, selected)

        # Chess.com brown
        # Color.WHITE: ("#f0d9b5", "#f8ec5a"),
        # Color.BLACK: ("#b58863", "#dac431"),

        # Chess.com green
        Color.WHITE: ("#eeeed3", "#f8f685"),
        Color.BLACK: ("#769656", "#bbc93f"),
    }

    root: tk.Tk
    pov: Color
    n_row: int
    n_col: int
    squares: list[list[tk.Canvas]]
    imgs: list[list[Optional[ImageTk.PhotoImage]]]
    move_fr: Optional[Coord]
    move_to: Optional[Coord]
    moved_to: Optional[Coord]
    moved_fr: Optional[Coord]

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Star Chess")
        self.root.geometry(
            f"{FrontendFancyGUI.window_dim[0]}x{FrontendFancyGUI.window_dim[1]}"
        )
        self.root.aspect(1, 1, 1, 1)

        self.squares = []
        self.imgs = []

        self.move_fr = None
        self.move_to = None
        self.moved_fr = None
        self.moved_to = None
    
    @property
    def cell_w(self):
        return self.window_dim[0] // self.n_col

    @property
    def cell_h(self):
        return self.window_dim[1] // self.n_row
    
    def povr(self, r):
        return r if self.pov is Color.BLACK else (self.n_row - 1 - r)
    
    def povc(self, c):
        return c if self.pov is Color.BLACK else (self.n_col - 1 - c)

    def povrc(self, coord: Coord):
        return Coord(self.povr(coord.r), self.povc(coord.c))
    
    def square_of_coord(self, coord: Coord) -> tk.Canvas:
        return self.squares[self.povr(coord.r)][self.povc(coord.c)]

    def img_of_coord(self, coord: Coord) -> ImageTk.PhotoImage:
        return self.imgs[self.povr(coord.r)][self.povc(coord.c)]

    def set_img_at_coord(self, coord: Coord, img: ImageTk.PhotoImage):
        self.imgs[self.povr(coord.r)][self.povc(coord.c)] = img
    
    def deselect_coord(self, coord: Coord, override = False):
        if not override and (
            (self.moved_fr is not None and self.moved_fr == coord) or
            (self.moved_to is not None and self.moved_to == coord)
        ):
            return
        self.square_of_coord(coord).configure(
            background=FrontendFancyGUI.hex_codes[
                    self.color_of_coord(coord)][0]
        )

    def select_coord(self, coord: Coord):
        self.square_of_coord(coord).configure(
            background=FrontendFancyGUI.hex_codes[
                    self.color_of_coord(coord)][1]
        )
    
    def coord_of_cell(self, cell: tk.Frame) -> Optional[Coord]:
        for r in range(self.n_row):
            for c in range(self.n_col):
                if cell is self.squares[r][c]:
                    return self.povrc(Coord(r, c))
        return None

    @staticmethod
    def color_of_coord(coord: Coord) -> Color:
        return (
            Color.WHITE
            if (coord.r % 2) ^ (coord.c % 2) == 0 else
            Color.BLACK
        )

    def display_init(self, state: State):
        self.pov = state.pov
        self.n_row = len(state.board.board)
        self.n_col = len(state.board.board[0])

        for r in range(self.n_row):
            self.root.rowconfigure(r, weight=FrontendFancyGUI.cell_weight)
        
        for c in range(self.n_col):
            self.root.columnconfigure(c, weight=FrontendFancyGUI.cell_weight)

        for r in range(self.n_row):
            self.squares.append(list())
            self.imgs.append(list())

            for c in range(self.n_col):
                color = FrontendFancyGUI.color_of_coord(Coord(r, c))

                background_color = FrontendFancyGUI.hex_codes[color][0]

                self.squares[-1].append(tk.Canvas(
                    self.root,
                    background=background_color,
                    highlightthickness=0
                ))
                self.squares[-1][-1].grid(
                    row=r,
                    column=c,
                    padx=FrontendFancyGUI.cell_padding,
                    pady=FrontendFancyGUI.cell_padding,
                    sticky="nsew"
                )

                self.imgs[-1].append(None)

        self.root.bind(
            "<Button-1>", lambda event: self.on_click(False, event))
        self.root.bind(
            "<Shift-Button-1>", lambda event: self.on_click(True, event))

        self.display_update(state, None)

    def display_update(self, state: State, changed: Optional[set[Coord]]):
        if self.move_fr is not None:
            dummy = tk.Event()
            dummy.widget = self.square_of_coord(self.move_fr)
            self.on_click(False, dummy)
        
        if self.moved_fr is not None:
            self.deselect_coord(self.moved_fr, override=True)
            self.moved_fr = None
        
        if self.moved_to is not None:
            self.deselect_coord(self.moved_to, override=True)
            self.moved_to = None
        
        if changed is not None and len(changed) == 2:
            list_changed = list(changed)
            self.moved_fr, self.moved_to = list_changed[0], list_changed[1]
            if state.board.board[self.moved_to.r][self.moved_to.c] is None:
                self.moved_fr, self.moved_to = self.moved_to, self.moved_fr
            self.select_coord(self.moved_fr)
            self.select_coord(self.moved_to)

        for r in range(self.n_row):
            for c in range(self.n_col):
                coord = Coord(r, c)

                if changed is not None and coord not in changed:
                    continue
                
                self.square_of_coord(coord).delete("all")

                piece = state.board.board[r][c]

                if piece is not None:
                    self.set_img_at_coord(
                        coord,
                        ImageTk.PhotoImage(
                            Image.open(piece.img_path).resize(
                                (self.cell_w, self.cell_h),
                                Image.ANTIALIAS
                            )
                        )
                    )
                    self.square_of_coord(coord).create_image(
                        self.cell_w // 2, self.cell_h // 2,
                        image=self.img_of_coord(coord)
                    )
                else:
                    self.set_img_at_coord(coord, None)
                
                self.square_of_coord(coord).update()

    def on_click(self, shift_held, event: tk.Event):
        clicked_coord = self.coord_of_cell(event.widget)

        if clicked_coord is None:
            return
        
        if shift_held:
            if self.move_fr is None or clicked_coord == self.move_fr:
                return
    
            if self.move_to is not None:
                self.deselect_coord(self.move_to)

            self.select_coord(clicked_coord)            
            self.move_to = clicked_coord
            
            return

        if self.move_fr is not None:
            self.deselect_coord(self.move_fr)

            if self.move_to is not None:
                self.deselect_coord(self.move_to)
                self.move_to = None

            if self.square_of_coord(self.move_fr) is event.widget:
                # this was an un-select
                self.move_fr = None
                return
        
        self.select_coord(clicked_coord)
        self.move_fr = clicked_coord

    def display_end(self):
        self.root.quit()
        self.root.destroy()
