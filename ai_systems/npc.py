from ollama_integration import interactive_dialogue, generate_dialogue
from dataclasses import dataclass
from typing import Dict, List
import json

# Define a simple data class to represent a Non-Player Character (NPC)
@dataclass
class NPC:
    id: str
    name: str
    background: str
    personality: str
    memories: List[Dict] = None

    def __post_init__(self):
        self.memories = self.memories or []

    def talk(self, player_input: str = None) -> str:
        """Handle both interactive and single-turn dialogue"""
        if player_input is None:
            # Launch a live dialogue loop with memory awareness
            interactive_dialogue(
                npc_id=self.id,
                npc_name=self.name,
                npc_background=f"{self.background}. Personality: {self.personality}"
            )
            return ""
        else:
            # Generate a one-time response based on input and personality
            return generate_dialogue(
                npc_name=self.name,
                situation=f"Personality: {self.personality}. {player_input}"
            )

# Class for managing multiple NPCs stored in a JSON file
class NPCHandler:
    def __init__(self, file_path: str = "data/npcs/npc_storage.json"):
        self.npcs: Dict[str, NPC] = {}
        self.file_path = file_path
        self.load_npcs()

    def load_npcs(self):
        try:
            with open(self.file_path) as f:
                data = json.load(f)
                for npc_id, npc_data in data.items():
                    self.npcs[npc_id] = NPC(
                        id=npc_id,
                        name=npc_data['name'],
                        background=npc_data['background'],
                        personality=npc_data.get('personality', 'neutral'),
                        memories=npc_data.get('memories', [])
                    )
        except FileNotFoundError:
            print(f"NPC storage not found at {self.file_path}")

    def save_npcs(self):
        data = {
            npc.id: {
                "name": npc.name,
                "background": npc.background,
                "personality": npc.personality,
                "memories": npc.memories[-10:]  # Keep last 10 memories
            }
            for npc in self.npcs.values()
        }
        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=2)

    def get_npc(self, key: str):
        key_norm = key.lower().replace(" ", "_")
        if key_norm in self.npcs:
            return self.npcs[key_norm]
        for npc in self.npcs.values():
            if npc.name.lower().replace(" ", "_") == key_norm:
                return npc
        return None


