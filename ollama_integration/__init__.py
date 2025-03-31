import ollama
from typing import Optional, Dict, List, Union
import time
import random
import json

OLLAMA_MODEL = "llama3.2"
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds
MAX_MEMORY_EXCHANGES = 5

FALLBACK_RESPONSES = {
    "dialogue": [
        "I can't think of anything to say right now.",
        "The NPC stares at you silently.",
        "Hmm... let me think about that."
    ],
    "description": [
        "A mysterious place with an eerie atmosphere.",
        "You can't quite make out the details in the dim light.",
        "The room feels ordinary, yet somehow unsettling."
    ],
    "name": [
        "Forgotten Chamber",
        "Mysterious Alcove",
        "Ancient Hall"
    ],
    "combat": [
        "The enemy prepares an attack!",
        "Your opponent circles warily.",
        "Combat continues..."
    ]
}

NPC_MEMORY: Dict[str, List[Dict]] = {}  # {npc_id: [{"player": "...", "npc": "..."}]}
ROOM_MEMORY: Dict[str, List[str]] = {}  # {room_id: ["generated_description"]}


def generate_structured_response(
        prompt: str,
        model: str = OLLAMA_MODEL,
        response_format: str = "text",
        temperature: float = 0.7,
        max_length: int = 150
) -> Union[str, Dict, None]:
    """
    Enhanced query function with retries, format handling, and length control

    Args:
        prompt: Input prompt for the model
        model: Which Ollama model to use
        response_format: "text" or "json"
        temperature: Creativity level (0.0-1.0)
        max_length: Maximum response length in tokens

    Returns:
        Response text, parsed JSON, or None if failed
    """
    for attempt in range(MAX_RETRIES):
        try:
            response = ollama.chat(
                model=model,
                messages=[{
                    'role': 'user',
                    'content': prompt,
                    'options': {
                        'temperature': temperature,
                        'num_ctx': max_length
                    }
                }]
            )
            content = response['message']['content'].strip()

            if response_format == "json":
                if content.startswith('```json'):
                    content = content[7:-3].strip()
                return json.loads(content)
            return content

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))

    print("Max retries reached for Ollama query")
    return None


def generate_dialogue(
        npc_name: str,
        npc_background: str,
        player_input: str,
        context: str = "",
        memory: List[Dict] = None
) -> str:
    """
    Generate contextual NPC dialogue with memory and personality

    Args:
        npc_name: Name/role of the NPC
        npc_background: Background/character traits
        player_input: What the player said
        context: Current game situation
        memory: Previous conversation turns

    Returns:
        Generated response or fallback
    """
    memory_context = "\n".join(
        f"Player: {m['player']}\n{npc_name}: {m['npc']}"
        for m in (memory or [])[-3:]  # Last 3 exchanges
    )

    prompt = f"""Roleplay as {npc_name}, a {npc_background} in a fantasy RPG.

Character Guidelines:
- Stay completely in character
- Respond naturally in 1-2 sentences
- Match the NPC's personality
- Never break the fourth wall

Current Situation:
{context}

Previous Conversation:
{memory_context if memory else "No prior interaction"}

Player says: "{player_input}"
{npc_name}:"""

    response = generate_structured_response(prompt, temperature=0.8)
    if response:
        response = response.split('\n')[0].replace('"', '')
        return response

    return random.choice(FALLBACK_RESPONSES["dialogue"])


def generate_room_content(
        room_type: str,
        theme: str,
        connected_rooms: List[str],
        existing_descriptions: List[str] = None
) -> Dict:
    """
    Generate comprehensive room content with thematic consistency

    Returns:
        Dict with:
        - description
        - name
        - features
        - mood
        - lore (optional)
    """
    prompt = f"""Generate descriptive content for a {room_type} in a {theme} dungeon.

Connected Rooms: {', '.join(connected_rooms[:3]) if connected_rooms else "None"}
Existing Descriptions: {existing_descriptions or "None"}

Required JSON format:
{{
    "name": "Creative room name (2-3 words)",
    "description": "Vivid 2-3 sentence description",
    "features": ["list", "of", "notable", "features"],
    "mood": "room atmosphere",
    "lore": "optional lore fragment"
}}"""

    try:
        content = generate_structured_response(prompt, response_format="json", temperature=0.6)
        if not content:
            raise ValueError("Empty response")

        for field in ["name", "description", "features", "mood"]:
            if field not in content:
                content[field] = f"Unknown {field}"

        return content
    except Exception as e:
        print(f"Room generation failed: {e}")
        return {
            "name": f"{theme} {room_type}",
            "description": random.choice(FALLBACK_RESPONSES["description"]),
            "features": ["Strange markings", "Unusual sounds"],
            "mood": "eerie"
        }


def interactive_dialogue(
        npc_id: str,
        npc_name: str,
        npc_background: str,
        context: str = ""
) -> None:
    """
    Start an interactive conversation with an NPC
    """
    if npc_id not in NPC_MEMORY:
        NPC_MEMORY[npc_id] = []

    memory = NPC_MEMORY[npc_id][-MAX_MEMORY_EXCHANGES:]

    greeting = generate_dialogue(
        npc_name,
        npc_background,
        "",
        context,
        memory
    )
    print(f"\n[{npc_name}]: {greeting or 'Greetings, traveler.'}")

    while True:
        try:
            player_input = input("\nYou: ").strip()
            if not player_input:
                continue

            if any(word in player_input.lower() for word in ["bye", "goodbye", "leave"]):
                farewell = generate_dialogue(
                    npc_name,
                    npc_background,
                    "goodbye",
                    context,
                    memory
                )
                print(f"\n[{npc_name}]: {farewell or 'Farewell.'}")
                NPC_MEMORY[npc_id].append({"player": player_input, "npc": "END_CONVERSATION"})
                break

            response = generate_dialogue(
                npc_name,
                npc_background,
                player_input,
                context,
                memory
            )
            print(f"\n[{npc_name}]: {response}")

            NPC_MEMORY[npc_id].append({"player": player_input, "npc": response})

        except KeyboardInterrupt:
            print(f"\n[{npc_name}]: *looks confused*")
            break


def generate_combat_action(
        enemy_type: str,
        combat_state: Dict,
        personality: str = "aggressive"
) -> str:
    """
    Generate AI-driven combat behavior

    Args:
        enemy_type: Type of enemy (goblin, skeleton, etc.)
        combat_state: Current combat status
        personality: Combat style (aggressive/defensive/tactical)
    """
    prompt = f"""As a {enemy_type} in combat, choose your next action.

Combat State:
- Player HP: {combat_state.get('player_hp', '?')}
- Enemy HP: {combat_state.get('enemy_hp', '?')}
- Available Actions: {combat_state.get('actions', [])}

Personality: {personality}
Respond ONLY with the action choice."""

    response = generate_structured_response(prompt, temperature=0.3)
    if response and response.lower() in combat_state.get('actions', []):
        return response.lower()

    if personality == "defensive":
        return random.choice(["block", "counter"])
    return random.choice(["attack", "special"])


def generate_puzzle(
        theme: str,
        difficulty: str = "medium",
        puzzle_type: str = None
) -> Dict:
    """
    Generate a complete puzzle with solution and hints

    Returns:
        Dict with:
        - description
        - solution
        - hints []
        - reward
    """
    prompt = f"""Create a {difficulty} {puzzle_type or 'riddle'} puzzle for a {theme} dungeon.

Format as JSON with:
- "description": "Puzzle presentation",
- "solution": "exact answer",
- "hints": ["progressive", "hints"],
- "reward": "item_id" """

    try:
        puzzle = generate_structured_response(prompt, response_format="json", temperature=0.5)
        if not puzzle:
            raise ValueError("Empty puzzle response")

        required = ["description", "solution", "hints", "reward"]
        return {k: puzzle.get(k, "Unknown") for k in required}
    except Exception as e:
        print(f"Puzzle generation failed: {e}")
        return {
            "description": "Solve the ancient riddle.",
            "solution": "time",
            "hints": ["It waits for no man", "The answer is fundamental"],
            "reward": "mysterious_key"
        }


def generate_quest(
        npc_name: str,
        npc_role: str,
        player_level: int = 1
) -> Dict:
    """
    Generate a complete quest with objectives

    Returns:
        Dict with:
        - title
        - description
        - objectives []
        - reward
    """
    prompt = f"""Create a quest for level {player_level} given by {npc_name}, a {npc_role}.

Format as JSON with:
- "title": "Quest name",
- "description": "2-3 sentence hook",
- "objectives": ["task", "list"],
- "reward": {{"item": "id", "xp": number}} """

    try:
        quest = generate_structured_response(prompt, response_format="json", temperature=0.6)
        if not quest:
            raise ValueError("Empty quest response")

        if "reward" not in quest:
            quest["reward"] = {"item": "gold_coins", "xp": player_level * 50}

        return quest
    except Exception as e:
        print(f"Quest generation failed: {e}")
        return {
            "title": f"{npc_name}'s Request",
            "description": "An important task needs completing.",
            "objectives": ["Find the lost artifact"],
            "reward": {"item": "small_pouch", "xp": 100}
        }

def generate_room_description(room_type: str, existing_rooms: List[str]) -> str:
    """Generate immersive room descriptions with contextual awareness"""
    prompt = f"""Generate a vivid 1-2 sentence description for a {room_type} in a fantasy dungeon.

Connected Rooms: {', '.join(existing_rooms[:3]) if existing_rooms else "None"}

Requirements:
- Include sensory details (sounds, smells, textures)
- Hint at possible secrets
- Match the dungeon's overall tone"""

    response = generate_structured_response(prompt)
    return response or random.choice(FALLBACK_RESPONSES["description"])


def generate_room_name(room_type: str, theme: str) -> str:
    prompt = f"""Generate a short, punchy name (2-3 words max) for a {room_type} in a {theme} dungeon.

Examples:
- "Chamber of Whispers" 
- "Forsaken Altar"
- "Halls of Decay"

Respond ONLY with the name, no other text:"""

    response = generate_structured_response(prompt)
    if response:
        response = response.split('\n')[0].strip('"\'')
        if len(response.split()) <= 3:
            return response

    return random.choice(FALLBACK_RESPONSES["name"])