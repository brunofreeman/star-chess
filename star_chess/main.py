import sys
from game import Game
from player import PlayerOnlineFancyGUI, PlayerOnlineOpponent
from frontend import FrontendFancyGUI
from state.entities.color.color import Color


def main(argv):
    color = Color(int(argv[1]))

    frontend = FrontendFancyGUI()

    user = PlayerOnlineFancyGUI(color, frontend)

    print(f"You are playing as {color.name}.")

    game = Game(
        "./spec/standard.json",
        user,
        PlayerOnlineOpponent(Color.other(color)),
        frontend
    )

    print("Game loaded. Starting game loop...")

    game.play()


if __name__ == "__main__":
    main(sys.argv)
