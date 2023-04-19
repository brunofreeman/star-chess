from abc import ABC, abstractmethod
from state.state import State

class Frontend(ABC):
    @abstractmethod
    def display_init(self):
        pass

    @abstractmethod
    def display_update(self, state: State):
        pass

    @abstractmethod
    def display_end(self):
        pass
