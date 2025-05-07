import json
import os

# Default file path for saving and loading game state
DEFAULT_SAVE_PATH = 'saves/savegame.json'

def save_game(game_data, filename=DEFAULT_SAVE_PATH):
    # Save the game data to a JSON file
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)  # Ensure save directory exists
        with open(filename, 'w') as f:
            json.dump(game_data, f, indent=2)  # Write data to file
        return True
    except Exception as e:
        print(f"Error saving game: {e}")
        return False

def load_game(filename=DEFAULT_SAVE_PATH):
    # Load game data from a JSON file
    try:
        if not os.path.exists(filename):
            return None  # Return None if file doesn't exist

        with open(filename, 'r') as f:
            return json.load(f)  # Load and return JSON content
    except Exception as e:
        print(f"Error loading game: {e}")
        return None