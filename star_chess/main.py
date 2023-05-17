import sys
from game import Game
from player import PlayerFancyGUI, PlayerRandomAI
from frontend import FrontendFancyGUI
from state.entities.color.color import Color


def main(argv):
    frontend = FrontendFancyGUI()

    user = PlayerFancyGUI(Color.random(), frontend)

    print(f"You are playing as {user.color.name}.")

    game = Game(
        "./spec/standard.json",
        user,
        PlayerRandomAI(Color.other(user.color)),
        frontend
    )

    print("Game loaded. Starting game loop...")

    game.play()


if __name__ == "__main__":
    main(sys.argv)
