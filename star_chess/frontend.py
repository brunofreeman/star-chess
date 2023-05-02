from abc import ABC, abstractmethod
import tkinter as tk
from state.state import State


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
