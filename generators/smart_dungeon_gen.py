import random
import json
from typing import Dict, List

from dungeon import Dungeon
from file_manager import FileManager
from ollama_integration import generate_structured_response, generate_room_description


class SmartDungeonGenerator:
    def __init__(self, dungeon: Dungeon):
        self.dungeon = dungeon
        self.file_manager = FileManager()
        self.themes = [
            "ancient cursed city",
            "forgotten dwarven kingdom",
            "volcanic caverns",
            "crystalline caves",
            "sunken elven ruins"
        ]
        self.current_theme = random.choice(self.themes)
        self.depth = 0
        self.room_archetypes = {
            'chamber': {'weight': 40, 'exits': (2, 4)},
            'hallway': {'weight': 25, 'exits': (1, 2)},
            'treasure': {'weight': 10, 'exits': (1, 2)},
            'shrine': {'weight': 15, 'exits': (1, 3)},
            'cavern': {'weight': 10, 'exits': (2, 3)}
        }

    def generate_new_room(self, connecting_room_id: str, direction: str) -> Dict:
        self.depth += 1
        connecting_room = self.dungeon.get_room(connecting_room_id)

        try:
            room_type = self._select_room_type(connecting_room)

            room_data = self._create_room_data(room_type, connecting_room)

            room_data['exits'] = self._generate_exits(
                room_data['id'],
                connecting_room_id,
                direction,
                room_type
            )

            self._populate_room(room_data)

            self.file_manager.write_json(f"data/dungeons/{room_data['id']}.json", room_data)
            return room_data

        except Exception as e:
            print(f"Generation error: {e}")
            return self._create_fallback_room(connecting_room_id, direction)

    def _select_room_type(self, connecting_room: Dict) -> str:
        prompt = f"""Given dungeon theme '{self.current_theme}' at depth {self.depth},
and previous room type '{connecting_room.get('type')}',
select the most appropriate room type from {list(self.room_archetypes.keys())}.

Consider:
- Deeper rooms should be more dangerous
- Maintain thematic consistency
- Create logical progression

Respond ONLY with the room type key."""

        try:
            response = generate_structured_response(prompt, temperature=0.3)
            return response.strip().lower()
        except:
            return random.choices(
                list(self.room_archetypes.keys()),
                weights=[a['weight'] for a in self.room_archetypes.values()],
                k=1
            )[0]

    def _create_room_data(self, room_type: str, connecting_room: Dict) -> Dict:
        context_rooms = [
                            r['name'] for r in self.dungeon.rooms.values()
                            if r['id'] != connecting_room['id']
                        ][-3:]

        try:
            room_data = generate_room_description(
                self.current_theme,
                room_type,
                context_rooms
            )
        except:
            room_data = self._basic_room_data(room_type)

        room_data.update({
            'id': f"{room_type}_{random.randint(1000, 9999)}",
            'type': room_type,
            'theme': self.current_theme,
            'depth': self.depth,
            'items': [],
            'npcs': [],
            'features': room_data.get('features', [])
        })

        return room_data

    def _generate_exits(self, room_id: str, connecting_id: str,
                        direction: str, room_type: str) -> Dict:
        opposites = {'north': 'south', 'south': 'north', 'east': 'west', 'west': 'east'}
        exits = {opposites[direction]: connecting_id}

        min_exits, max_exits = self.room_archetypes[room_type]['exits']
        target_exits = random.randint(min_exits, max_exits)

        if self.depth > 5:
            target_exits = min(target_exits + 1, 4)

        possible_directions = [d for d in ['north', 'south', 'east', 'west']
                               if d != opposites[direction]]

        for _ in range(target_exits - 1):
            if not possible_directions:
                break

            new_dir = random.choice(possible_directions)

            rand = random.random()
            if rand < 0.6:
                exits[new_dir] = f"unexplored_{new_dir}_{room_id}"
            elif rand < 0.9:
                exits[new_dir] = {
                    'type': 'hidden',
                    'clue': random.choice([
                        f"faint draft from the {new_dir}",
                        f"unusual markings pointing {new_dir}"
                    ])
                }
            else:
                exits[new_dir] = {
                    'type': 'blocked',
                    'description': f"collapsed passage to the {new_dir}"
                }

            possible_directions.remove(new_dir)

        return exits

    def _populate_room(self, room_data: Dict):
        room_data['items'] = self._generate_items(room_data['type'])

        if random.random() < 0.4:
            room_data['npcs'] = self._generate_npcs(room_data['type'])

        if room_data['type'] in ['shrine', 'treasure'] and random.random() < 0.3:
            room_data['puzzle'] = self._generate_puzzle()

    def _generate_items(self, room_type: str) -> List[str]:
        item_lists = {
            'chamber': ['torch', 'journal', 'broken weapon'],
            'hallway': ['pebble', 'old coin', 'rusty key'],
            'treasure': ['gem', 'gold idol', 'ancient artifact'],
            'shrine': ['holy symbol', 'offerings', 'candle'],
            'cavern': ['crystal', 'strange moss', 'fossil']
        }
        items = []
        for item in item_lists.get(room_type, []):
            if random.random() < 0.5:
                items.append(item)
        return items

    def _generate_npcs(self, room_type: str) -> List[Dict]:
        npc_types = {
            'chamber': ['lost explorer', 'undead guardian'],
            'hallway': ['patrolling creature', 'fleeing adventurer'],
            'treasure': ['greedy thief', 'guardian spirit'],
            'shrine': ['wandering priest', 'cursed worshipper'],
            'cavern': ['cave dweller', 'mineral hunter']
        }
        npc = random.choice(npc_types.get(room_type, ['mysterious figure']))
        return [{
            'id': f"npc_{random.randint(1000, 9999)}",
            'name': npc,
            'dialogue': f"Ask me about the {self.current_theme}",
            'attitude': random.choice(['friendly', 'neutral', 'hostile'])
        }]

    def _generate_puzzle(self) -> Dict:
        puzzles = [
            {
                'description': "A riddle is inscribed on the wall",
                'solution': "time",
                'hint': "It waits for no man",
                'reward': 'ancient_key'
            },
            {
                'description': "Symbols must be pressed in order",
                'solution': "moon,star,sun",
                'hint': "Follow the night sky",
                'reward': 'enchanted_gem'
            }
        ]
        return random.choice(puzzles)

    def _basic_room_data(self, room_type: str) -> Dict:
        return {
            'name': f"{self.current_theme} {room_type}",
            'description': f"A {room_type} in the {self.current_theme}.",
            'features': [
                "Strange markings",
                "Unusual sounds",
                "Odd smells"
            ],
            'mood': random.choice(['eerie', 'calm', 'tense'])
        }

    def _create_fallback_room(self, connecting_id: str, direction: str) -> Dict:
        opposites = {'north': 'south', 'south': 'north', 'east': 'west', 'west': 'east'}
        return {
            'id': f"fallback_{random.randint(1000, 9999)}",
            'type': 'chamber',
            'name': 'Collapsed Passage',
            'description': 'This area shows signs of structural damage.',
            'exits': {opposites[direction]: connecting_id},
            'items': ['torch'] if random.random() < 0.5 else [],
            'npcs': [],
            'features': ['cracked walls', 'loose stones'],
            'depth': self.depth
        }