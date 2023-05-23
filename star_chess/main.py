import sys
from game import Game
from player import PlayerOnlineFancyGUI, PlayerOnlineOpponent
from frontend import FrontendFancyGUI
from state.entities.color.color import Color


def usage(argv):
    print(f"usage: {argv[0]} --color={{w,b}} [--username=<username> --opponent=<opponent>]")
    sys.exit(1)


def parse_args(argv):
    if len(argv) == 2 or len(argv) == 4:
        if argv[1] == "--color=w":
            color = Color.WHITE
        elif argv[1] == "--color=b":
            color = Color.BLACK
        else:
            usage(argv)
    else:
        usage(argv)
    
    username = None
    opponent = None

    if len(argv) == 4:
        if (
            not argv[2].startswith("--username=") or
            not argv[3].startswith("--opponent=")
        ):
            usage(argv)
        
        if argv[2] == "--username=" or argv[3] == "--opponent":
            usage(argv)
        
        username = argv[2].split("--username")[1][1:]
        opponent = argv[3].split("--opponent")[1][1:]

    return color, username, opponent


def main(argv):
    color, username, opponent = parse_args(argv)

    frontend = FrontendFancyGUI()

    user = PlayerOnlineFancyGUI(color, frontend, username, opponent)

    game = Game(
        "./spec/standard.json",
        user,
        PlayerOnlineOpponent(Color.other(color), opponent),
        frontend
    )

    game.play()


if __name__ == "__main__":
    main(sys.argv)
