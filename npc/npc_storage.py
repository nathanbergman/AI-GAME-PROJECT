import json

# File path for storing NPC data
NPC_STORAGE_PATH = '../data/npcs/npc_storage.json'

def load_npcs():
    # Load all NPCs from the JSON file
    try:
        with open(NPC_STORAGE_PATH, 'r') as file:
            npcs = json.load(file)
    except FileNotFoundError:
        npcs = []  # Return empty list if file doesn't exist
    return npcs

def save_npcs(npcs):
    # Save the NPC list to the JSON file
    with open(NPC_STORAGE_PATH, 'w') as file:
        json.dump(npcs, file, indent=4)

def add_npc(npc):
    # Add a new NPC and save the updated list
    npcs = load_npcs()
    npcs.append(npc)
    save_npcs(npcs)

def get_npc_by_name(npc_name):
    # Find an NPC by name from the stored list
    npcs = load_npcs()
    for npc in npcs:
        if npc['name'] == npc_name:
            return npc
    return None  # Return None if not found