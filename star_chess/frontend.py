from abc import ABC, abstractmethod
from typing import Optional
import tkinter as tk
from state.state import State
from state.entities.color.color import Color
from state.entities.move.coord import Coord


class Frontend(ABC):
    @abstractmethod
    def display_init(self, state: State):
        pass

    @abstractmethod
    def display_update(self, state: State):
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

    def display_update(self, state: State):
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
        Color.BLACK: ("#b58863", "#dac431"),
        Color.WHITE: ("#f0d9b5", "#f8ec5a")
    }

    root: tk.Tk
    cells: list[list[tk.Frame]]
    selected: Optional[Coord]

    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry(
            f"{FrontendFancyGUI.window_dim[0]}x{FrontendFancyGUI.window_dim[1]}"
        )
        self.root.aspect(1, 1, 1, 1)
        self.root.title("Star Chess")
        self.cells = []
        self.selected = None

    def display_init(self, state: State):
        for r in range(len(state.board.board)):
            self.root.rowconfigure(r, weight=FrontendFancyGUI.cell_weight)
        
        for c in range(len(state.board.board[0])):
            self.root.columnconfigure(c, weight=FrontendFancyGUI.cell_weight)

        row_start_color = Color.BLACK
        for r in range(len(state.board.board)):
            color = row_start_color
            self.cells.append(list())

            for c in range(len(state.board.board[0])):
                self.cells[-1].append(tk.Frame(self.root))

                self.cells[-1][-1].grid(
                    row=r,
                    column=c,
                    padx=FrontendFancyGUI.cell_padding,
                    pady=FrontendFancyGUI.cell_padding,
                    sticky="nsew"
                )

                self.cells[-1][-1].configure(
                    background=(
                        FrontendFancyGUI.hex_codes[Color.WHITE][0]
                        if color is Color.WHITE else
                        FrontendFancyGUI.hex_codes[Color.BLACK][0]
                    )
                )
    
                color = Color.other(color)

            row_start_color = Color.other(row_start_color)

        self.root.bind(
            "<Button-1>", lambda event: self.on_click(False, event))
        self.root.bind(
            "<Shift-Button-1>", lambda event: self.on_click(True, event))

        self.display_update(state)

    def display_update(self, state: State):
        pass

    def display_end(self):
        self.root.quit()
        self.root.destroy()
    
    def coord_of_cell(self, cell: tk.Frame) -> Optional[Coord]:
        for r in range(len(self.cells)):
            for c in range(len(self.cells[0])):
                if cell is self.cells[r][c]:
                    return Coord(r, c)
        return None

    def color_of_coord(self, coord: Coord) -> Color:
        return (
            Color.WHITE
            if (coord.r % 2) ^ (coord.c % 2) == 1 else
            Color.BLACK
        )

    def on_click(self, shift_held, event):
        clicked_coord = self.coord_of_cell(event.widget)
        if clicked_coord is None:
            return

        if self.selected is not None:
            cell = self.cells[self.selected.r][self.selected.c]
            cell.configure(
                background=FrontendFancyGUI.hex_codes[
                    self.color_of_coord(self.selected)][0]
            )

            if cell is event.widget:
                self.selected = None
                return
        
        self.selected = clicked_coord

        event.widget.configure(
            background=FrontendFancyGUI.hex_codes[
                    self.color_of_coord(self.selected)][1]
        )
