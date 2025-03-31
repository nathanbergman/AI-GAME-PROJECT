import json
import os

DEFAULT_SAVE_PATH = 'saves/savegame.json'


def save_game(game_data, filename=DEFAULT_SAVE_PATH):
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(game_data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving game: {e}")
        return False


def load_game(filename=DEFAULT_SAVE_PATH):
    try:
        if not os.path.exists(filename):
            return None

        with open(filename, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading game: {e}")
        return None


def delete_save(filename=DEFAULT_SAVE_PATH):
    try:
        if os.path.exists(filename):
            os.remove(filename)
            return True
        return False
    except Exception as e:
        print(f"Error deleting save: {e}")
        return False