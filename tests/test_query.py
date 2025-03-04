import json

with open("test.json", "r") as stream:
    v = json.load(stream)
    print(v)