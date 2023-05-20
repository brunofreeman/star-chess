import requests

url = "https://www.tylerdnguyen.com/scserver/post"

data = {
    "int": 42,
    "list": [3, 1, 4],
    "str": "lorem ipsum"
}

print("== sent ==")
print(data)
print()

response = requests.post(
    url,
    data=data
)

print("== received ==")
print(response)
print(response.text)
