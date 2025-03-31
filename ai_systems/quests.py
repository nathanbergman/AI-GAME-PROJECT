from ollama_integration import generate_structured_response
from dataclasses import dataclass
from typing import List, Dict
import json


@dataclass
class Quest:
    id: str
    title: str
    description: str
    objectives: List[Dict]
    reward: Dict


class QuestGenerator:
    def __init__(self, npc_handler):
        self.npc_handler = npc_handler

    def generate_quest(self, npc_id: str) -> Quest:
        npc = self.npc_handler.get_npc(npc_id)
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
            response = generate_structured_response(prompt)
            data = json.loads(response.strip("```json\n").strip("```"))
            return Quest(
                id=f"quest_{npc_id}_{hash(response)}",
                **data
            )
        except Exception as e:
            print(f"Quest generation failed: {e}")
            return self._fallback_quest(npc)

    def _fallback_quest(self, npc) -> Quest:
        return Quest(
            id=f"quest_{npc.id}_fallback",
            title=f"{npc.name}'s Request",
            description=f"{npc.name} needs your help with something important.",
            objectives=[{"description": "Discover what the NPC wants", "completed": False}],
            reward={"item": "small_pouch", "xp": 100}
        )