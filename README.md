# star-chess

## Dependencies
`star-chess` requires [`tkinter`](https://docs.python.org/3/library/tkinter.html)
and [`pillow`](https://pillow.readthedocs.io/en/stable/reference/ImageTk.html).
`tkinter` is part of the base Python installation, but you will need to
`{pip, pip3} install pillow`. The code uses `match`/`case`, a relatively new
Python 3 feature, so you may need to update Python if you see an error reported
on these keywords.

## Usage

1. Navigate to the `star_chess/` directory.
2. Run `python3 main.py --color={w,b} [--username=u --opponent=o]`, where:
    1. `w`/`b` indicates that you are playing as white/black, respectively.
    2. `u` and `o` are your and your opponent's usernames, respectively.
        1. Usernames should not contain spaces
        (e.g. `--username=c3po --opponent=r2d2`).
        2. If not specified, the usernames default to `WHITE` or `BLACK`, as
        appropriate based on the `--color` argument. This option is only
        provided to facilitate more rapid testing. On Ditch Day, usernames
        should be specified and must be unique.

**Important:** successful networking relies on good-faith coordination between
clients. If

```python3 main.py --color=w --username=luke --opponent=leia```

is run on one computer, then

```python3 main.py --color=b --username=leia --opponent=luke```

must be run on another computer to properly initiate the game (i.e., both
colors and usernames must be properly coordinated). In addition, **usernames
should be unique across all simultaneous games**. If `luke` and `leia` are
actively playing a game, it would corrupt server state to start another game
that also uses either of these usernames.

## Misc

### Application not responding!
Opponent moves are fetched from the server by polling the server and then, in
the case the opponent hasn't moved yet, sleeping for a few seconds before
trying again. During this sleep, the OS will indicate that the program has
become unresponsive if you attempt to interact with the GUI. This is expected
and is just a remnant of not having enough time to do it a better way. On
Windows, the entire GUI will be shaded in a white overlay if you click it,
which is especially concerning. Everything should snap back to responsiveness
once the opponent moves.
