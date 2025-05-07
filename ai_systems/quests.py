from ollama_integration import generate_structured_response
from dataclasses import dataclass
from typing import List, Dict
import json

# Data class for storing quest information
@dataclass
class Quest:
    id: str
    title: str
    description: str
    objectives: List[Dict]
    reward: Dict

# Class for generating quests using AI
class QuestGenerator:
    def __init__(self, npc_handler):
        self.npc_handler = npc_handler  # Reference to the NPC handler

    def generate_quest(self, npc_id: str) -> Quest:
        npc = self.npc_handler.get_npc(npc_id)  # Fetch NPC info
        # Prompt to generate quest data
        prompt = f"""Create a fantasy RPG quest given by {npc.name}, a {npc.background}.

Required JSON format:
{{
    "title": "Creative quest name",
    "description": "2-3 sentence hook",
    "objectives": [
        {{"description": "clear objective", "completed": false}}
    ],
    "reward": {{
        "item": "useful_item_id",
        "xp": 50-200
    }}
}}"""

        try:
            response = generate_structured_response(prompt)  # Call AI to generate quest
            data = json.loads(response.strip("```json\n").strip("```"))  # Parse JSON
            return Quest(
                id=f"quest_{npc_id}_{hash(response)}",  # Unique ID using hash
                **data
            )
        except Exception as e:
            print(f"Quest generation failed: {e}")  # Log failure
            return self._fallback_quest(npc)  # Use fallback if needed

    def _fallback_quest(self, npc) -> Quest:
        # Return a default quest if AI generation fails
        return Quest(
            id=f"quest_{npc.id}_fallback",
            title=f"{npc.name}'s Request",
            description=f"{npc.name} needs your help with something important.",
            objectives=[{"description": "Discover what the NPC wants", "completed": False}],
            reward={"item": "small_pouch", "xp": 100}
        )