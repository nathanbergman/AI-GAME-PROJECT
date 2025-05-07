from ollama_integration import generate_structured_response
from typing import Dict, Optional
import random

class PuzzleGenerator:
    def __init__(self, difficulty: str = "medium"):
        self.difficulty = difficulty  # Set puzzle difficulty
        self.puzzle_types = ["riddle", "pattern", "physical", "logic"]  # Types of puzzles

    def generate_puzzle(self, theme: str) -> Dict:
        # Prompt to generate puzzle content based on dungeon theme and difficulty
        prompt = f"""Create a {self.difficulty} difficulty {random.choice(self.puzzle_types)} puzzle for a {theme}-themed dungeon.

Format as JSON with:
- "description": string (what player sees)
- "solution": string (exact answer)
- "hints": list[str] (3 progressively clearer hints)
- "reward": string (item ID)"""

        try:
            response = generate_structured_response(prompt, model="llama3")  # Query Ollama
            return self._validate_puzzle(response)
        except Exception as e:
            print(f"Puzzle generation failed: {e}")  # Log error if generation fails
            return self._fallback_puzzle(theme)  # Return fallback puzzle

    def _validate_puzzle(self, response: str) -> Dict:
        # Strip formatting and parse the response
        puzzle = eval(response.strip("```json\n").strip("```"))
        required = ["description", "solution", "hints", "reward"]
        return {k: puzzle.get(k, "Error") for k in required}  # Return validated fields

    def _fallback_puzzle(self, theme: str) -> Dict:
        # Default puzzle if generation fails
        return {
            "description": f"Solve the ancient {theme} riddle.",
            "solution": "knowledge",
            "hints": [
                "Look to the past for answers",
                "The solution is a fundamental concept",
                "The answer is 'knowledge'"
            ],
            "reward": "scroll_" + theme
        }