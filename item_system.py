import json
import os

class ItemSystem:
    def __init__(self, items_file=None):
        self.items_file = items_file
        self.items = {}
        if self.items_file and os.path.exists(self.items_file):
            self.load_items_from_file(self.items_file)
        else:
            self.initialize_default_items()

    def initialize_default_items(self):
        self.items = {
            'torch': {
                'id': 'torch',
                'name': 'Torch',
                'description': 'A basic torch that provides light in dark areas.',
                'type': 'tool',
                'usable': True,
                'effect': 'light'
            },
            'sword': {
                'id': 'sword',
                'name': 'Sword',
                'description': 'An sword that might be effective in combat.',
                'type': 'weapon',
                'attack_bonus': 2,
                'equippable': True,
                'usable': False
            },
            'gold_coins': {
                'id': 'gold_coins',
                'name': 'Gold Coins',
                'description': 'A pile of glittering gold coins.',
                'type': 'misc',
                'usable': False,
                'value': 100
            },
            'health_potion': {
                'id': 'health_potion',
                'name': 'Health Potion',
                'description': 'A potion that restores 25 health points.',
                'type': 'consumable',
                'usable': True,
                'effect': 'heal',
                'potency': 25
            }
        }

    def load_items_from_file(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.items = json.load(f)
        except Exception:
            self.initialize_default_items()

    def save_items_to_file(self, filename=None):
        target_file = filename or self.items_file
        if not target_file:
            return False
        try:
            with open(target_file, 'w', encoding='utf-8') as f:
                json.dump(self.items, f, indent=2)
            return True
        except Exception:
            return False

    def get_item(self, item_id):
        return self.items.get(item_id)

    def add_item(self, item_data):
        item_id = item_data.get('id')
        if not item_id:
            return False
        self.items[item_id] = item_data
        return True

    def remove_item(self, item_id):
        if item_id in self.items:
            del self.items[item_id]
            return True
        return False

    def update_item(self, item_id, updates):
        if item_id not in self.items:
            return False
        self.items[item_id].update(updates)
        return True

    def list_items(self):
        return list(self.items.keys())
