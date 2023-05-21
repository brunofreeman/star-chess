import requests
import json
import sys

url = "https://www.tylerdnguyen.com/scserver/post"

match int(sys.argv[1]):
    case -2:
        data = {
            "int": 42,
            "list": [3, 1, 4],
            "str": "lorem ipsum"
        }
    
    case -1:
        data = {
            "action": "clear",
            "username": "white"
        }

    case 0:
        data = {
            "action": "clear",
            "username": "black"
        }

    case 1:
        data = {
            "action": "submit",
            "username": "white",
            "move": {
                "fr": [0, 1],
                "to": [2, 3]
            },
            "key": "move-001"
        }

    case 2:
        data = {
            "action": "query",
            "username": "white",
            "key": "move-001"
        }
    
    case 3:
        data = {
            "action": "submit",
            "username": "black",
            "move": {
                "fr": [4, 5],
                "to": [6, 7]
            },
            "key": "move-002"
        }

    case 4:
        data = {
            "action": "query",
            "username": "black",
            "key": "move-002"
        }

    case 5:
        data = {
            "action": "submit",
            "username": "white",
            "move": {
                "fr": [8, 9],
                "to": [0, 1]
            },
            "key": "move-003"
        }

    case 6:
        data = {
            "action": "query",
            "username": "white",
            "key": "move-003"
        }
    
    case 7:
        data = {
            "action": "query",
            "username": "white",
            "key": "move-999"
        }

    case _:
        print(f"invalid option '{sys.argv[1]}'")
        exit()

print("== sent ==")
print(data)
print()

response = requests.post(
    url,
    data=json.dumps(data),
    headers={
        "content-type": "application/json"
    }
)

print("== received ==")
print(response)
try:
    print(json.dumps(json.loads(response.text), indent=4))
except:
    print(response.text)
print()
