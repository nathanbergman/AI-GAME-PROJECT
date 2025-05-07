import pathlib
import os
from character import Player
from dungeon import Dungeon
from file_manager import FileManager
from game_state import save_game, load_game
from generators.smart_dungeon_gen import SmartDungeonGenerator
from ollama_integration import interactive_dialogue, generate_dialogue
from ai_systems.npc import NPCHandler
from ai_systems.quests import Quest, QuestGenerator
from ai_systems.puzzles import PuzzleGenerator
from ai_systems.combat import TacticalCombatAI
from Spell_system import SpellSystem
import random
import time

class DungeonMaster:
    def __init__(self):

        self.game_root = pathlib.Path(__file__).parent
        self.dungeons_dir = self.game_root / "data" / "dungeons"
        self.npcs_dir = self.game_root / "data" / "npcs"
        self.saves_dir = self.game_root / "saves"
        self.file_manager = FileManager(self.game_root)
        self.dungeon = Dungeon(self.file_manager)
        self.player = None
        self.dungeon = Dungeon()
        self.current_room = None
        self.game_active = False
        self.room_generator = SmartDungeonGenerator(self.dungeon)
        self.discovered_rooms = set()
        npc_file = self.file_manager.npcs_path / "npc_storage.json"
        if not npc_file.exists():
            npc_file.write_text("{}", encoding="utf-8")
        self.npc_handler = NPCHandler(str(npc_file))
        print("DEBUG npc_handler keys =", list(self.npc_handler.npcs.keys()))
        print("DEBUG npc_file =", npc_file)
        self.quest_system = QuestGenerator(self.npc_handler)
        self.current_quest = None
        self.puzzle_system = PuzzleGenerator()
        self.combat_ai = TacticalCombatAI()
        self.combat_active = False
        
    def start_new_game(self):
        print("\n=== DUNGEON ADVENTURE ===")
        print("A text adventure of exploration and mystery\n")

        player_name = input("Enter your character's name: ").strip()
        while not player_name:
            player_name = input("Please enter a valid name: ").strip()
        ## Choose from one of three classes, with error checking
        print("Classes:\n1.Fighter\n2.Wizard\n3.Paladin\n\nChoose a character class: ")
        while True: 
            try: 
                player_class_int = int(input())
                while not player_class_int or player_class_int <= 0 or player_class_int > 3:
                    player_class_int = int(input("Please enter a valid number: "))
                break
            except ValueError:
                print("That is not a number!")
        ##class array
        Classes = ["Fighter", "Wizard", "Paladin"]

        self.player = Player(player_name, Classes[player_class_int-1])
        self.current_room = self.dungeon.get_room("entrance")
        self.game_active = True
        self.discovered_rooms = {self.current_room['id']}
        self.SpellSystem = SpellSystem(self.player)
        print(f"\nWelcome, {player_name}! Your adventure begins...")
        time.sleep(1)
        print("You find yourself standing at the entrance to a long-forgotten dungeons.")
        time.sleep(1)
        print("The air is stale, and the only sounds are your footsteps and distant drips of water.\n")
        time.sleep(1)
        self.describe_current_room()

    def load_game(self):
        data = load_game()
        if not data:
            print("\nNo saved game found or save file corrupted.")
            print("Starting a new game instead...")
            time.sleep(2)
            self.start_new_game()
            return

        try:
            self.player = Player(data['player']['name'], data['player']['class'])
            stats = {
                'health': (100, 200),
                'max_health': (100, 200),
                'base_attack': (5, 30),
                'base_defense': (5, 30),
                'experience': (0, 10000),
                'level': (1, 50)
            }

            for stat, (min_val, max_val) in stats.items():
                if stat in data['player']:
                    setattr(self.player, stat, max(min_val, min(max_val, data['player'][stat])))

            self.player.inventory = [item for item in data['player'].get('inventory', [])
                                     if isinstance(item, dict) and 'id' in item]

            self.dungeon = Dungeon()
            self.room_generator = SmartDungeonGenerator(self.dungeon)
            self.SpellSystem = SpellSystem(self.player)

            if 'discovered_rooms' in data:
                for room_id in data['discovered_rooms']:
                    if room_id not in self.dungeon.rooms:
                        try:
                            room_data = self.file_manager.read_json(f"{room_id}.json")
                            if room_data:
                                self.dungeon.add_dynamic_room(room_data)
                        except:
                            pass

            self.current_room = self.dungeon.get_room(data['current_room'])
            if not self.current_room:
                print("Warning: Saved room not found. Starting from entrance.")
                self.current_room = self.dungeon.get_room("entrance")
                
            self.game_active = True
            self.discovered_rooms = set(data.get('discovered_rooms', [self.current_room['id']]))


            print("\nGame loaded successfully!")
            time.sleep(1)
            self.describe_current_room()

        except Exception as e:
            print(f"\nFailed to load game data: {str(e)}")
            print("Starting a new game instead...")
            time.sleep(2)
            self.start_new_game()

    def describe_current_room(self):
        """Display immersive room description"""
        print(f"\n=== {self.current_room['name'].upper()} ===")

        room_type = self.current_room.get('type', 'chamber')
        type_descriptions = {
            'entrance': "The way out is behind you...",
            'chamber': "The chamber echoes with your footsteps.",
            'hallway': "The narrow passage constricts around you.",
            'treasure': "Something valuable might be hidden here.",
            'shrine': "A sense of reverence fills the air.",
            'cavern': "The natural formations create eerie shadows."
        }

        print(self.current_room['description'])
        print(f"\n{type_descriptions.get(room_type, '')}")

        if 'features' in self.current_room and self.current_room['features']:
            print("\nNotable features:")
            for feature in self.current_room['features']:
                print(f"- {feature.capitalize()}")

        if 'items' in self.current_room and self.current_room['items']:
            print("\nItems here:")
            for item_id in self.current_room['items']:
                item = self.dungeon.get_item(item_id)
                if item:
                    print(f"- {item['name']}")

        if 'npcs' in self.current_room and self.current_room['npcs']:
            print("DEBUG current_room['npcs'] =", self.current_room['npcs'])
            print("\nYou see:")
            for npc_id in self.current_room['npcs']:
                npc = self.dungeon.get_npc(npc_id)
                if npc:
                    print(f"- {npc['name']}: {npc.get('description', '')}")

        if 'exits' in self.current_room and self.current_room['exits']:
            exits = list(self.current_room['exits'].keys())
            exit_text = ", ".join(exits[:-1]) + f" and {exits[-1]}" if len(exits) > 1 else exits[0]
            print(f"\nExits to the {exit_text}")

    def _resolve_npc(self, key: str):
        key_norm = key.lower().replace(" ", "_")

        for npc_id in self.current_room.get("npcs", []):
            
            npc_obj = self.npc_handler.get_npc(npc_id)
            if not npc_obj:
                continue
            if npc_id == key_norm:
                return npc_id
            if npc_obj.name.lower().replace(" ", "_") == key_norm:
                return npc_id
        return None

    def process_command(self, command):
        cmd = command.lower().strip()

        if not cmd:
            return "Please enter a command."

        # Combat commands
        if self.combat_active:
            if cmd in ['attack', 'block', 'use', 'flee']:
                return self.handle_combat_action(cmd)
            return "Combat commands: attack, block, use [item], flee"

        # Movement commands
        if cmd in ['north', 'south', 'east', 'west']:
            return self.move_player(cmd)
        elif cmd.startswith('go '):
            direction = cmd[3:].strip()
            if direction in ['north', 'south', 'east', 'west']:
                return self.move_player(direction)
            return "Invalid direction. Use north/south/east/west."

        # Inventory management
        elif cmd == 'inventory':
            return self.show_inventory()
        elif cmd.startswith('take '):
            return self.take_item(cmd[5:].strip())
        elif cmd.startswith('drop '):
            return self.drop_item(cmd[5:].strip())
        elif cmd.startswith('use '):
            return self.use_item(cmd[4:].strip())
        elif cmd.startswith('equip '):
            return self.equip_item(cmd[6:].strip())
        elif cmd.startswith('examine '):
            return self.examine_item(cmd[8:].strip())
        elif cmd.startswith('cast '):
            return self.cast_spell(cmd[5:].strip())
        
        #character Sheet
        elif cmd == 'sheet':
            return self.show_sheet()
        # Exploration
        elif cmd == 'search':
            return self.search_room()
        elif cmd == 'look':
            self.describe_current_room()
            return ""
        elif cmd == 'map':
            return self.show_map()

        # Character actions
        elif cmd == 'rest':
            return self.rest_action()
        elif cmd == 'stats':
            return self.show_stats()

        # NPC Interactions
        elif cmd.startswith('talk to '):
            npc_raw = cmd[8:].strip()
            npc_id = self._resolve_npc(npc_raw)
            if npc_id:
                return self.handle_npc_conversation(npc_id)
            return f"No {npc_raw} here to talk to."

        elif cmd.startswith('ask '):
            npc_raw = cmd[4:].strip()
            npc_id = self._resolve_npc(npc_raw)
            if npc_id:
                return self.handle_npc_question(npc_id)
            return f"No {npc_raw} here to ask."


        # Quest System
        elif cmd == 'quest':
            return self.show_quest_status()
        elif cmd.startswith('accept quest from '):
            npc_name = cmd[18:].strip()
            return self.start_quest(npc_name)

        # Puzzle System
        elif cmd == 'solve puzzle':
            if 'puzzle' in self.current_room:
                solution = input("Enter your solution: ")
                return self.attempt_puzzle(solution)
            return "No active puzzle here."

        # Game management
        elif cmd == 'save':
            return self.save_game_state()
        elif cmd in ['quit', 'exit']:
            return self.quit_game()
        elif cmd == 'help':
            return self.show_help()

        
        else:
            similar = self.find_similar_commands(cmd)
            if similar:
                return f"Unknown command. Did you mean: {', '.join(similar)}?"
            return "I don't understand that command. Type 'help' for options."

    def move_player(self, direction):
        if direction not in ['north', 'south', 'east', 'west']:
            return "Invalid direction. Use north/south/east/west."

        try:
            if direction in self.current_room.get('exits', {}):
                next_room_id = self.current_room['exits'][direction]

                if isinstance(next_room_id, str) and next_room_id.startswith('unexplored_'):
                    print(f"\nYou carefully explore the {direction} passage...")
                    time.sleep(1)

                    new_room = self.room_generator.generate_new_room(
                        self.current_room['id'],
                        direction
                    )

                    self.current_room['exits'][direction] = new_room['id']
                    self.dungeon.add_dynamic_room(new_room)
                    next_room_id = new_room['id']

                self.current_room = self.dungeon.get_room(next_room_id)
                self.discovered_rooms.add(next_room_id)

                #print(f"\n=== {self.current_room['name'].upper()} ===")
                self.describe_current_room()
                return ""

            print("\nYou search the walls and discover a hidden passage!")
            time.sleep(1)

            new_room = self.room_generator.generate_new_room(
                self.current_room['id'],
                direction
            )
            self.current_room['exits'][direction] = new_room['id']
            self.dungeon.add_dynamic_room(new_room)

            self.current_room = new_room
            self.discovered_rooms.add(new_room['id'])

            print(f"\nDiscovered: {new_room['name']}")
            self.describe_current_room()
            return ""

        except Exception as e:
            print(f"\nAn error occurred while moving: {str(e)}")
            print("You stumble but remain in the current room.")
            return ""

    def handle_npc_conversation(self, npc_name: str):
        npc = self.npc_handler.get_npc(npc_name)
        if not npc:
            return f"No {npc_name} here to talk to."

        print(f"\n=== Conversation with {npc.name} ===")
        interactive_dialogue(
            npc_id=npc.id,
            npc_name=npc.name,
            npc_background=f"{npc.background}. Personality: {npc.personality}"
        )
        self.npc_handler.save_npcs()
        return ""

    def handle_npc_question(self, npc_name: str):
        npc = self.npc_handler.get_npc(npc_name)
        if not npc:
            return f"No {npc_name} here to ask."

        question = input(f"What would you like to ask {npc.name}? ")
        response = npc.talk(question)
        return f"\n{npc.name}: {response}"

    def start_quest(self, npc_name: str):
        if self.current_quest:
            return "Finish your current quest first."

        npc = self.npc_handler.get_npc(npc_name)
        if not npc:
            return f"No {npc_name} here to get a quest from."

        self.current_quest = self.quest_system.generate_quest(npc.id)
        return (f"New Quest: {self.current_quest.title}\n"
                f"{self.current_quest.description}\n"
                f"First Objective: {self.current_quest.objectives[0]['description']}")

    def show_quest_status(self):
        if not self.current_quest:
            return "You don't have an active quest."

        objectives = "\n".join(
            f"{'✓' if obj['completed'] else '☐'} {obj['description']}"
            for obj in self.current_quest.objectives
        )
        return (f"=== {self.current_quest.title.upper()} ===\n"
                f"{objectives}\n\n"
                f"Reward: {self.current_quest.reward['item']} + {self.current_quest.reward['xp']} XP")

    def attempt_puzzle(self, solution: str):
        if 'puzzle' not in self.current_room:
            return "Nothing to solve here."

        puzzle = self.current_room['puzzle']
        if solution.lower() == puzzle['solution'].lower():
            self.player.inventory.append(puzzle['reward'])
            del self.current_room['puzzle']
            return (f"Correct! {puzzle['success_message']}\n"
                    f"Received: {puzzle['reward']['name']}")
        return random.choice(puzzle['failure_messages'])

    def handle_combat_action(self, action: str):
        if not self.combat_active:
            return "Not in combat!"

        enemy = self.current_room['enemy']
        outcome = ""

        if action == 'attack':
            damage = max(1, self.player.base_attack - random.randint(0, enemy.defense))
            enemy.health -= damage
            outcome = f"You hit {enemy.name} for {damage} damage!"
        elif action == 'block':
            self.player.defense += 2
            outcome = "You raise your guard (+2 defense this turn)"
        elif action.startswith('use '):
            outcome = self.use_item(action[4:], combat=True)
        elif action == 'flee':
            if random.random() < 0.7:
                self.combat_active = False
                return "You successfully flee from combat!"
            outcome = "Failed to escape!"

        if enemy.health <= 0:
            self.combat_active = False
            xp = enemy.xp_reward
            self.player.experience += xp
            return (f"You defeated {enemy.name}!\n"
                    f"Gained {xp} XP.\n"
                    f"{self.check_level_up()}")

        enemy_action = self.combat_ai.decide_action({
            'player_hp': self.player.health,
            'enemy_hp': enemy.health,
            'enemy_type': enemy.type,
            'available_actions': enemy.actions
        })

        if enemy_action == 'attack':
            damage = max(1, enemy.attack - random.randint(0, self.player.base_defense))
            self.player.health -= damage
            outcome += f"\n{enemy.name} hits you for {damage} damage!"
        elif enemy_action == 'special':
            pass

        return outcome

    def check_level_up(self):
        needed = self.player.level * 100
        if self.player.experience >= needed:
            self.player.level += 1
            self.player.max_health += 10
            self.player.health = self.player.max_health
            return f"Level up! Reached level {self.player.level}!"
        return ""

    def generate_room_puzzle(self):
        if 'puzzle' not in self.current_room and random.random() < 0.4:
            theme = self.current_room.get('type', 'ancient')
            puzzle = self.puzzle_system.generate_puzzle(theme)
            self.current_room['puzzle'] = puzzle

    def generate_discovery_event(self, room):
        events = {
            'chamber': [
                "Dust falls from the ceiling as you enter.",
                "Ancient carvings seem to watch your movements."
            ],
            'hallway': [
                "A cold draft sends chills down your spine.",
                "Your footsteps echo ominously in the narrow space."
            ],
            'treasure': [
                "Something glints in the darkness...",
                "Your pulse quickens - this place might hold riches!"
            ],
            'shrine': [
                "A sense of reverence fills you as you enter.",
                "Strange energies tingle at your skin."
            ],
            'cavern': [
                "The air here is damp and earthy.",
                "Strange mineral deposits glitter in your torchlight."
            ]
        }

        room_type = room.get('type', 'chamber')
        if random.random() < 0.7:
            print(f"\n{random.choice(events.get(room_type, ['Something feels different here...']))}")
            time.sleep(1)

        if random.random() < 0.3:
            if random.random() < 0.5 and 'items' not in room:
                room['items'] = [random.choice(['health_potion', 'torch', 'gold_coins'])]
                print("\nYou spot something on the ground!")
            elif 'npcs' not in room:
                room['npcs'] = [random.choice(['lost_adventurer', 'friendly_ghost'])]
                print("\nSomeone else is here!")

    def show_help(self):
            return """
    === COMMAND REFERENCE ===

Movement:
  north/south/east/west - Move 
  go [direction]        - Same as above
  look                  - Examine room
  search                - Find hidden items
  map                   - Show explored areas

Inventory:
  inventory             - View items
  take/drop [item]      - Manage items
  use [item]            - Use consumables
  equip [item]          - Equip gear
  examine [item]        - Inspect items

Character Sheet:
sheet                   - Examine your character

Combat:
  attack                - Basic attack
  block                 - Raise defense
  use [item]            - Use item in combat
  flee                  - Attempt escape

NPC Interaction:
  talk to [name]        - Start conversation
  ask [name]            - Ask one question
  accept quest from [npc] - Get new quest

Quests & Puzzles:
  quest                 - Show current quest
  solve puzzle          - Attempt room puzzle

Game:
  save                  - Save progress
  help                  - Show this
  quit/exit             - Quit game

Tip: Many commands can be abbreviated (n/s/e/w, inv, exa)
    """
    def show_sheet(self):
        output = "=== CHARACTER SHEET ===\n"
        output = f"{output}\n Name: {self.player.name}"
        output = f"{output}\n Class: {self.player.className}\n Level : {self.player.level}\n Experience: {self.player.experience}"
        if self.player.max_mana > 0:
            output = f"{output}\n Mana: {self.player.mana}/{self.player.max_mana}"
        output = f"{output}\n Attack: {self.player.base_attack}"
        output = f"{output}\n Defense: {self.player.base_defense}"

        output = f"{output}\n Health: {self.player.health}/{self.player.max_health}"
        return output
    def show_inventory(self):
            if not self.player.inventory:
                return "Your inventory is empty."

            equipped = []
            carried = []

            for item in self.player.inventory:
                if item == self.player.equipped.get('weapon') or item == self.player.equipped.get('armor'):
                    equipped.append(item)
                else:
                    carried.append(item)

            output = ["=== INVENTORY ==="]

            if equipped:
                output.append("\nEquipped:")
                for item in equipped:
                    slot = "weapon" if item == self.player.equipped.get('weapon') else "armor"
                    output.append(f"- {item['name']} ({slot})")

            if carried:
                output.append("\nCarrying:")
                for item in carried:
                    output.append(f"- {item['name']}")
                    if 'description' in item:
                        output.append(f"  {item['description']}")

            return "\n".join(output)

    def search_room(self):
            if random.random() < 0.2:
                items = {
                    'chamber': ['gold coin', 'old key', 'gemstone', 'dusty scroll'],
                    'hallway': ['loose brick', 'broken weapon', 'torn map'],
                    'treasure': ['hidden gem', 'ancient coin', 'silver locket'],
                    'shrine': ['holy symbol', 'blessed water', 'sacred text'],
                    'cavern': ['glowing crystal', 'strange mushroom', 'fossil']
                }

                room_type = self.current_room.get('type', 'chamber')
                found_item = random.choice(items.get(room_type, ['mysterious object']))
                self.player.inventory.append({'name': found_item, 'type': 'misc'})

                descriptions = {
                    'gold coin': "You spot something shiny under some debris.",
                    'old key': "Your hand brushes against metal in a crevice.",
                    'gemstone': "A glint catches your eye from a shadowy corner.",
                    'dusty scroll': "You find a rolled parchment tucked in a crack.",
                    'mysterious object': "You uncover something unusual."
                }

                return f"{descriptions.get(found_item, 'You find something hidden.')}\nFound: {found_item.capitalize()}!"

            return random.choice([
                "You search carefully but find nothing of value.",
                "The search reveals only dust and cobwebs.",
                "Nothing catches your interest.",
                "If there's anything here, it's well hidden."
            ])

    def rest_action(self):
            

            recovery = min(15, self.player.max_health - self.player.health)
            self.player.health += recovery
            self.player.base_attack -= self.player.floatingA
            self.player.base_defense -= self.player.floatingD
            self.player.mana = self.player.max_mana
            room_type = self.current_room.get('type', 'chamber')
            descriptions = {
                'chamber': "You sit against the cold stone wall and catch your breath.",
                'hallway': "You pause in the narrow passage to rest briefly.",
                'treasure': "You take a moment to rest amidst the dusty riches.",
                'shrine': "The peaceful atmosphere helps you recover.",
                'cavern': "The quiet drip of water accompanies your rest."
            }

            return f"{descriptions.get(room_type, 'You take a moment to rest.')}\nRecovered {recovery} HP and {self.player.mana} mana."

    def show_stats(self):
            attack = self.player.base_attack
            defense = self.player.base_defense

            if self.player.equipped.get('weapon'):
                attack += self.player.equipped['weapon'].get('attack_bonus', 0)
            if self.player.equipped.get('armor'):
                defense += self.player.equipped['armor'].get('defense_bonus', 0)

            next_level = self.player.level * 100
            progress = min(100, int((self.player.experience / next_level) * 100)) if next_level > 0 else 0

            return f"""
    === {self.player.name.upper()} ===
    Health: {self.player.health}/{self.player.max_health}
    Attack: {attack} (base: {self.player.base_attack})
    Defense: {defense} (base: {self.player.base_defense})
    Level: {self.player.level}
    Progress: {progress}% to next level
    Discovered: {len(self.discovered_rooms)} rooms
    """

    def examine_item(self, item_name):
        inventory_item = next((i for i in self.player.inventory
                                   if i['name'].lower() == item_name.lower()), None)
        if inventory_item:
            desc = inventory_item.get('description', 'A mysterious item of unknown purpose.')
            details = ""

            if inventory_item.get('type') == 'weapon':
                details = f"\nAttack bonus: +{inventory_item.get('attack_bonus', 0)}"
            elif inventory_item.get('type') == 'armor':
                details = f"\nDefense bonus: +{inventory_item.get('defense_bonus', 0)}"
            elif inventory_item.get('type') == 'consumable':
                effect = inventory_item.get('effect', 'unknown')
                details = f"\nEffect: {effect}"
                if effect == 'heal':
                    details += f" ({inventory_item.get('potency', 0)} HP)"

            return f"=== {inventory_item['name'].upper()} ===\n{desc}{details}"

        if 'items' in self.current_room:
            for item_id in self.current_room['items']:
                item = self.dungeon.get_item(item_id)
                if item and item['name'].lower() == item_name.lower():
                    return f"You examine {item['name']}:\n{item.get('description', 'It looks interesting.')}"

        return f"You don't see {item_name} here."

    def take_item(self, item_name):
        if 'items' not in self.current_room or not self.current_room['items']:
            return "There's nothing here to take."

        for i, item_id in enumerate(self.current_room['items']):
            item = self.dungeon.get_item(item_id)
            if item and item['name'].lower() == item_name.lower():
                if len(self.player.inventory) >= 10:
                    return "Your inventory is full! Drop something first."

                del self.current_room['items'][i]
                self.player.inventory.append(item)

                take_messages = [
                    f"You pick up the {item['name']}.",
                    f"The {item['name']} goes into your pack.",
                    f"You take the {item['name']}.",
                    f"Added {item['name']} to inventory."
                ]
                return random.choice(take_messages)

        return f"You don't see {item_name} here."

    def drop_item(self, item_name):
        item = next((i for i in self.player.inventory
                        if i['name'].lower() == item_name.lower()), None)
        if not item:
            return f"You're not carrying {item_name}."

        if item == self.player.equipped.get('weapon'):
            self.player.equipped['weapon'] = None
        elif item == self.player.equipped.get('armor'):
            self.player.equipped['armor'] = None

        self.player.inventory.remove(item)
        if 'items' not in self.current_room:
            self.current_room['items'] = []
        self.current_room['items'].append(item['id'])

        return f"You drop the {item['name']}."

    def use_item(self, item_name):
        item = next((i for i in self.player.inventory
                        if i['name'].lower() == item_name.lower()), None)
        if not item:
            return f"You're not carrying {item_name}."

        if not item.get('usable', False):
            return f"You can't use the {item['name']}."

        if item['type'] == 'consumable':
            if item['effect'] == 'heal':
                before = self.player.health
                self.player.health = min(self.player.max_health,
                                            self.player.health + item.get('potency', 0))
                recovered = self.player.health - before
                self.player.inventory.remove(item)
                return (f"You use the {item['name']} and recover {recovered} HP.\n"
                        f"Health: {before} → {self.player.health}/{self.player.max_health}")

        elif item['type'] == 'tool':
            if item['id'] == 'torch':
                return "The torch burns steadily, illuminating your surroundings."

        return f"You use the {item['name']}, but nothing noticeable happens."

    def equip_item(self, item_name):
        item = next((i for i in self.player.inventory
                        if i['name'].lower() == item_name.lower()), None)
        if not item:
            return f"You're not carrying {item_name}."

        if not item.get('equippable', False):
            return f"You can't equip the {item['name']}."

        slot = 'weapon' if item['type'] == 'weapon' else 'armor'
        currently_equipped = self.player.equipped.get(slot)

        self.player.equipped[slot] = item

        if currently_equipped:
            return (f"You swap {currently_equipped['name']} for {item['name']}.\n"
                    f"Equipped {item['name']} as {slot}.")
        return f"Equipped {item['name']} as {slot}."

    def find_similar_commands(self, input_cmd):
        commands = {
            'movement': ['north', 'south', 'east', 'west', 'go'],
            'inventory': ['take', 'drop', 'use', 'equip', 'examine', 'inventory'],
            'game': ['look', 'search', 'rest', 'stats', 'save', 'help', 'quit']
        }

        suggestions = []
        input_cmd = input_cmd.lower()

        for category in commands.values():
            for cmd in category:
                if input_cmd in cmd or cmd.startswith(input_cmd):
                    suggestions.append(cmd)

        return suggestions[:3]

    def quit_game(self):
        print("\nAre you sure you want to quit? (y/n)")
        if input().lower() == 'y':
            print("\nWould you like to save before quitting? (y/n)")
            if input().lower() == 'y':
                print(self.save_game_state())
            self.game_active = False
            return "Goodbye! Your adventure awaits..."
        return "Resuming your adventure..."

    def save_game_state(self):
        save_data = {
            'player': {
                'name': self.player.name,
                'class': self.player.className,
                'health': self.player.health,
                'max_health': self.player.max_health,
                'base_attack': self.player.base_attack,
                'base_defense': self.player.base_defense,
                'inventory': self.player.inventory,
                'experience': self.player.experience,
                'level': self.player.level
            },
            'current_room': self.current_room['id'],
            'discovered_rooms': list(self.discovered_rooms)
        }

        if hasattr(self.dungeon, 'dynamic_rooms'):
            for room_id, room_data in self.dungeon.dynamic_rooms.items():
                try:
                    self.file_manager.write_json(f"{room_id}.json", room_data)
                except Exception as e:
                    print(f"Error saving dynamic room {room_id}: {e}")

        if save_game(save_data):
            return "Game saved successfully!"
        return "Failed to save game."
    def cast_spell(self, spellName):
        self.SpellSystem.cast_spell(spellName)
    def show_map(self):
        if not self.discovered_rooms:
            return "You haven't discovered any areas yet."

        map_text = "\n=== DISCOVERED AREAS ===\n"
        for room_id in self.discovered_rooms:
            room = self.dungeon.get_room(room_id)
            if room:
                map_text += f"- {room['name']}\n"

        return map_text + f"\nCurrently in: {self.current_room['name']}"

    def game_loop(self):
        print("\n=== DUNGEON ADVENTURE ===")
        print("1. New Game")
        print("2. Load Game")
        print("3. Quit")

        while True:
            choice = input("\nChoose an option (1-3): ").strip()
            if choice == '1':
                self.start_new_game()
                break
            elif choice == '2':
                self.load_game()
                if self.game_active:
                    break
            elif choice == '3':
                print("Goodbye!")
                return
            else:
                print("Please enter 1, 2, or 3.")

        while self.game_active:
            try:
                command = input("\nWhat would you like to do? ").strip()
                if not command:
                    continue

                result = self.process_command(command)
                if result:
                    print(result)

            except (KeyboardInterrupt, EOFError):
                print("\n\nGame paused. Save before quitting? (y/n)")
                if input().lower() == 'y':
                    print(self.save_game_state())
                self.game_active = False
            except Exception as e:
                print(f"\nAn error occurred: {str(e)}")
                print("The game will attempt to continue...")


if __name__ == "__main__":
    game = DungeonMaster()
    game.game_loop()