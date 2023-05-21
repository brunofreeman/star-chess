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
    selected_fr: Optional[Coord]
    move_fr: Optional[Coord]
    move_to: Optional[Coord]

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Star Chess")
        self.root.geometry(
            f"{FrontendFancyGUI.window_dim[0]}x{FrontendFancyGUI.window_dim[1]}"
        )
        self.root.aspect(1, 1, 1, 1)

        self.cells = []
        self.squares = []
        self.imgs = []
        self.selected_fr = None
        self.move_fr = None
        self.move_to = None
    
    @property
    def cell_w(self):
        return self.window_dim[0] // self.n_col

    @property
    def cell_h(self):
        return self.window_dim[1] // self.n_row
    
    def povr(self, r):
        return r if self.pov is Color.BLACK else (self.n_row - 1 - r)
    
    def coord_of_cell(self, cell: tk.Frame) -> Optional[Coord]:
        for r in range(self.n_row):
            for c in range(self.n_col):
                if cell is self.squares[r][c]:
                    return Coord(r, c)
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

                background_color = (
                    FrontendFancyGUI.hex_codes[Color.WHITE][0]
                    if color is Color.WHITE else
                    FrontendFancyGUI.hex_codes[Color.BLACK][0]
                )

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
        if self.selected_fr is not None:
            dummy = tk.Event()
            dummy.widget = self.squares[self.selected_fr.r][self.selected_fr.c]
            self.on_click(False, dummy)
        self.move_fr = None
        self.move_to = None

        for r in range(self.n_row):
            for c in range(self.n_col):
                if changed is not None and Coord(self.povr(r), c) not in changed:
                    continue

                piece = state.board.board[self.povr(r)][c]

                if piece is not None:
                    self.imgs[r][c] = ImageTk.PhotoImage(
                        Image.open(piece.img_path).resize(
                            (self.cell_w, self.cell_h),
                            Image.ANTIALIAS
                        )
                    )
                    self.squares[r][c].create_image(
                        self.cell_w // 2, self.cell_h // 2,
                        image=self.imgs[r][c])
                else:
                    self.imgs[r][c] = None
                    self.squares[r][c].delete("all")

    def on_click(self, shift_held, event: tk.Event):
        clicked_coord = self.coord_of_cell(event.widget)
        if clicked_coord is None:
            return
        
        if shift_held:
            if self.selected_fr is None or clicked_coord == self.selected_fr:
                return
            self.squares[clicked_coord.r][clicked_coord.c].configure(
                background=FrontendFancyGUI.hex_codes[
                        self.color_of_coord(clicked_coord)][1]
            )
            self.move_fr = Coord(
                self.povr(self.selected_fr.r), self.selected_fr.c)
            self.move_to = Coord(
                self.povr(clicked_coord.r), clicked_coord.c)
            return

        if self.selected_fr is not None:
            cell_fr = self.squares[self.selected_fr.r][self.selected_fr.c]
            cell_fr.configure(
                background=FrontendFancyGUI.hex_codes[
                    self.color_of_coord(self.selected_fr)][0]
            )

            if self.move_to is not None:
                crd = Coord(self.povr(self.move_to.r), self.move_to.c)
                self.squares[crd.r][crd.c].configure(
                    background=FrontendFancyGUI.hex_codes[
                            self.color_of_coord(crd)][0]
                )
                self.move_fr = None
                self.move_to = None

            if cell_fr is event.widget:
                self.selected_fr = None
                return
        
        self.selected_fr = clicked_coord

        event.widget.configure(
            background=FrontendFancyGUI.hex_codes[
                    self.color_of_coord(self.selected_fr)][1]
        )

    def display_end(self):
        self.root.quit()
        self.root.destroy()
