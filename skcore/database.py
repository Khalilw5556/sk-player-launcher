import json
import os

DB_PATH = os.path.join("data", "games.json")

def load_games():
    if not os.path.exists(DB_PATH):
        return []

    try:
        with open(DB_PATH, "r") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                return list(data.values())
            return []
    except (json.JSONDecodeError, IOError):
        return []

def save_games(games):
    if not os.path.exists("data"):
        os.makedirs("data")

    with open(DB_PATH, "w") as f:
        if not isinstance(games, list):
            games = []
        json.dump(games, f, indent=4)