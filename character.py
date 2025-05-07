from pathlib import Path
from file_manager import FileManager

# Base character class for players and NPCs
class Character:
    def __init__(self, name, health=100, attack=10, defense=5):
        self.name = name
        self.max_health = health
        self.health = health
        self.base_attack = attack
        self.base_defense = defense
        self.inventory = []
        self.equipped = {"weapon": None, "armor": None}  # Equipped gear

    @property
    def attack(self):
        # Total attack includes weapon bonus if equipped
        bonus = self.equipped["weapon"]["attack_bonus"] if self.equipped["weapon"] else 0
        return self.base_attack + bonus

    @property
    def defense(self):
        # Total defense includes armor bonus if equipped
        bonus = self.equipped["armor"]["defense_bonus"] if self.equipped["armor"] else 0
        return self.base_defense + bonus

    def take_damage(self, amount):
        # Apply damage after reducing with defense (min 1)
        actual_damage = max(1, amount - self.defense)
        self.health -= actual_damage
        return actual_damage

    def heal(self, amount):
        # Heal up to max health
        self.health = min(self.max_health, self.health + amount)

    def is_alive(self):
        return self.health > 0  # Check if character is alive

    def attack_target(self, target):
        # Attack another character and return damage dealt
        damage = self.attack
        if self.equipped["weapon"]:
            damage += self.equipped["weapon"].get("attack_bonus", 0)
        return target.take_damage(damage)

# Player character class with leveling and class data
class Player(Character):
    def __init__(self, name, player_class):
        super().__init__(name)
        self.file_manager = FileManager()  # Load class data
        self.experience = 0
        self.level = 1
        self.quests = []
        self.max_mana = 0
        self.mana = 0
        self.className = player_class
        class_filename = f"{player_class}.JSON"
        class_data = self.file_manager.read_json(self.file_manager.classes_path, class_filename)
        if not class_data:
            raise FileNotFoundError(f"Class file not found: {class_filename}")
        self.Classdata = class_data
        self.desc = self.Classdata["details"]["Description"]
        self.class_level_up(self.level)
        for startingItem in self.Classdata['StartingEquipment']:
            self.inventory.append(startingItem)

    def add_experience(self, amount):
        # Add XP and check for level up
        self.experience += amount
        if self.experience >= self.level * 100:
            self.level_up()

    def level_up(self):
        # Level up and apply base stat increases
        self.level += 1
        self.max_health += 10
        self.health = self.max_health
        self.base_attack += 2
        self.base_defense += 1
        self.class_level_up(self.level)

    def class_level_up(self, level):
        # Apply class-specific bonuses if not at max level
        if self.Classdata["details"]["max_Level"] < level:
            return
        self.max_health += self.Classdata["LevelUps"][level]["health"]
        self.health = self.max_health
        self.base_defense += self.Classdata["LevelUps"][level]["defense"]
        self.base_attack += self.Classdata["LevelUps"][level]["attack"]
        if self.Classdata["LevelUps"][level].get("mana"):
            self.max_mana += self.Classdata["LevelUps"][level]["mana"]
            self.mana = self.max_mana