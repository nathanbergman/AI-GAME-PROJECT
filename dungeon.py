from file_manager import FileManager
from item_system import ItemSystem
import random

class Dungeon:
    def __init__(self, file_manager: FileManager = None):
        self.file_manager = file_manager or FileManager()
        self.rooms = self.load_rooms()
        self.item_system = ItemSystem()
        self.dynamic_rooms = {}
        self._ensure_entrance_exists()

    def _ensure_entrance_exists(self):
        if "entrance" not in self.rooms:
            print("Warning: Entrance room not found - creating default")
            entrance = {
                "id": "entrance",
                "name": "Dungeon Entrance",
                "description": "A massive stone archway marks the entrance.",
                "type": "entrance",
                "exits": {"north": "hallway1"},
                "items": ["torch"],
                "features": ["carved runes"],
                "npcs": []
            }
            self.rooms["entrance"] = entrance
            self.file_manager.write_json("entrance.json", entrance)

    def load_rooms(self) -> dict:
        rooms = {}
        entrance_data = self.file_manager.read_json("entrance.json")
        if entrance_data:
            rooms["entrance"] = entrance_data

        for room_file in self.file_manager.list_dungeon_files():
            if room_file != "entrance.json":
                room_data = self.file_manager.read_json(room_file)
                if room_data:
                    rooms[room_data['id']] = room_data
        return rooms

    def validate_room(self, room_data):
        required_fields = {
            'id': lambda: room_data['id'],
            'type': lambda: room_data.get('type', 'chamber'),
            'name': lambda: room_data.get('name', 'Unnamed Room'),
            'description': lambda: room_data.get('description', 'A nondescript room.'),
            'exits': lambda: room_data.get('exits', {}),
            'items': lambda: room_data.get('items', []),
            'npcs': lambda: room_data.get('npcs', []),
            'features': lambda: room_data.get('features', [])
        }

        return {field: validator() for field, validator in required_fields.items()}

    def validate_connections(self, rooms):
        for room_id, room in rooms.items():
            valid_exits = {}
            for direction, target_id in room.get('exits', {}).items():
                if target_id.startswith('unexplored_'):
                    valid_exits[direction] = target_id
                elif target_id in rooms or target_id in self.dynamic_rooms:
                    valid_exits[direction] = target_id
                else:
                    print(f"Warning: Invalid exit in {room_id} - {direction} leads to non-existent room {target_id}")
            room['exits'] = valid_exits

    def get_room(self, room_id):
        room = self.rooms.get(room_id) or self.dynamic_rooms.get(room_id)

        if not room:
            print(f"Warning: Room {room_id} not found - generating fallback")
            room = {
                'id': room_id,
                'type': 'chamber',
                'name': 'Collapsed Passage',
                'description': 'This area appears partially collapsed, but you can make out some passages.',
                'exits': self.generate_fallback_exits(room_id),
                'items': [],
                'npcs': [],
                'features': ['crumbling walls']
            }
            self.dynamic_rooms[room_id] = room

        if not room.get('exits') and room.get('type') not in ['treasure', 'shrine']:
            direction = random.choice(['north', 'south', 'east', 'west'])
            room['exits'][direction] = f"unexplored_{direction}_{room_id}"

        return room

    def generate_fallback_exits(self, room_id):
        exits = {}
        for direction in random.sample(['north', 'south', 'east', 'west'], random.randint(1, 2)):
            exits[direction] = f"unexplored_{direction}_{room_id}"
        return exits

    def create_fallback_room(self, room_id, name):
        fallback = {
            'id': room_id,
            'type': 'chamber',
            'name': name,
            'description': 'This space seems unstable and unnatural.',
            'exits': {},
            'items': [],
            'npcs': [],
            'features': ['shifting walls']
        }
        self.dynamic_rooms[room_id] = fallback
        return fallback

    def add_dynamic_room(self, room_data):
        if not hasattr(self, 'dynamic_rooms'):
            self.dynamic_rooms = {}
        self.dynamic_rooms[room_data['id']] = room_data
        return room_data

    def connect_rooms(self, room1_id, room2_id, direction):
        try:
            room1 = self.get_room(room1_id)
            room2 = self.get_room(room2_id)

            if not room1 or not room2:
                return False

            opposite_dir = self.get_opposite_direction(direction)

            room1['exits'][direction] = room2_id
            room2['exits'][opposite_dir] = room1_id

            return True

        except Exception as e:
            print(f"Error connecting rooms: {e}")
            return False

    @staticmethod
    def get_opposite_direction(direction):
        opposites = {
            'north': 'south',
            'south': 'north',
            'east': 'west',
            'west': 'east',
            'up': 'down',
            'down': 'up'
        }
        return opposites.get(direction.lower(), direction)

    def get_item(self, item_id):
        try:
            return self.item_system.get_item(item_id)
        except Exception as e:
            print(f"Error getting item {item_id}: {e}")
            return None

    def save_dynamic_rooms(self):
        for room_id, room in self.dynamic_rooms.items():
            try:
                self.file_manager.write_json(f'dungeons/{room_id}.json', room)
            except Exception as e:
                print(f"Error saving room {room_id}: {e}")