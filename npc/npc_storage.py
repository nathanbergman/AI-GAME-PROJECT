import json

NPC_STORAGE_PATH = '../data/npcs/npc_storage.json'

def load_npcs():
    try:
        with open(NPC_STORAGE_PATH, 'r') as file:
            npcs = json.load(file)
    except FileNotFoundError:
        npcs = []
    return npcs

def save_npcs(npcs):
    with open(NPC_STORAGE_PATH, 'w') as file:
        json.dump(npcs, file, indent=4)

def add_npc(npc):
    npcs = load_npcs()
    npcs.append(npc)
    save_npcs(npcs)

def get_npc_by_name(npc_name):
    npcs = load_npcs()
    for npc in npcs:
        if npc['name'] == npc_name:
            return npc
    return None
