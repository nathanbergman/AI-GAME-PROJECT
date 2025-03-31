import json
from ollama_integration.__init__ import generate_dialogue


class NPCHandler:
    def __init__(self):
        self.npc_data = self.load_npc_data()

    def load_npc_data(self):
        try:
            with open('npcs.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "old_hermit": {
                    "name": "Old Hermit",
                    "description": "A wrinkled old man with a long beard",
                    "quest_giver": True,
                    "dialogue_style": "wise but cryptic"
                },
                "tavern_keep": {
                    "name": "Tavern Keep",
                    "description": "A burly woman wiping a mug",
                    "vendor": True,
                    "dialogue_style": "friendly but businesslike"
                }
            }

    def interact(self, npc_id, player):
        npc = self.get_npc(npc_id)
        if not npc:
            return "No one by that name is here."

        print(f"\nYou approach {npc['name']}.")

        context = f"{npc.get('description', '')}. {npc.get('dialogue_style', '')}"
        if npc.get('quest_giver', False):
            situation = f"The adventurer {player.name} approaches you about a quest"
        elif npc.get('vendor', False):
            situation = f"The adventurer {player.name} is looking to buy something"
        else:
            situation = f"The adventurer {player.name} is talking to you"

        dialogue = generate_dialogue(npc['name'], f"{context}. {situation}")
        print(f"\n{npc['name']} says: \"{dialogue}\"")

        if npc.get('quest_giver', False):
            return "Press 'q' to accept quest or any key to continue"
        elif npc.get('vendor', False):
            return "Press 'b' to browse wares or any key to continue"
        return "Press any key to continue"