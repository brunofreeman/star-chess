import requests
import json
import time
import os
from typing import Any, Optional
from state.entities.move.move import Move
from state.entities.move.coord import Coord


POST_ENDPOINT = "https://www.tylerdnguyen.com/scserver/post"
HEADERS = {
    "content-type": "application/json"
}
MOVE_PASS = "pass"
MOVE_FORFEIT = "forfeit"


def move_key(move_no: int) -> str:
    return f"move-{move_no:03d}"


def server_ok_or_fail(data: dict[str, Any]):
    response = requests.post(
        POST_ENDPOINT,
        data=json.dumps(data),
        headers=HEADERS
    )

    if not response.ok:
        raise ValueError(response.text)


def server_clear(username: str):
    server_ok_or_fail({
        "action": "clear",
        "username": username
    })


def server_submit(username: str, move: Optional[Move], move_no: int):
    if move is None:
        server_submit_special(username, MOVE_PASS, move_no)
    else:
        server_ok_or_fail({
            "action": "submit",
            "username": username,
            "move": {
                "fr": [move.fr.r, move.fr.c],
                "to": [move.to.r, move.to.c],
                "capture": move.capture
            },
            "key": move_key(move_no)
        })


def server_submit_special(username: str, move_special: str, move_no: int):
    if move_special not in (MOVE_PASS, MOVE_FORFEIT):
        raise ValueError(move_special)
    
    server_ok_or_fail({
        "action": "submit",
        "username": username,
        "move": move_special,
        "key": move_key(move_no)
    })


def server_query(username: str, move_no: int) -> tuple[Optional[Move], bool]:
    while True:
        os.system("sleep 3")

        response = requests.post(
            POST_ENDPOINT,
            data=json.dumps({
                "action": "query",
                "username": username,
                "key": move_key(move_no)
            }),
            headers=HEADERS
        )
        
        if response.status_code == 404:
            continue
        elif not response.ok:
            raise ValueError(response.text)
        else:
            moveData = json.loads(response.text)["move"]

            if moveData == MOVE_PASS:
                return None, False
            elif moveData == MOVE_FORFEIT:
                return None, True
            else:
                return Move(
                    Coord(*moveData["fr"]),
                    Coord(*moveData["to"]),
                    moveData["capture"],
                    None
                ), False
