import sys
from game import Game
from player import PlayerCLI, PlayerRandomAI
from frontend import FrontendTextGUI
from state.entities.color.color import Color


def main(argv):
    print("Loading game...")

    user = PlayerCLI(Color.random())

    print(f"You are playing as {user.color.name.lower()}.")

    game = Game(
        "./spec/simple.json",
        user,
        PlayerRandomAI(Color.other(user.color)),
        FrontendTextGUI()
    )

    print("Game loaded. Starting game loop...")

    game.play()


if __name__ == "__main__":
    main(sys.argv)
