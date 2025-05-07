# Import dependencies
from ollama_integration import generate_structured_response
from typing import Dict, List
import random


class TacticalCombatAI:
    # Set up difficulty flag and behaviour presets
    def __init__(self, difficulty: str = "normal"):
        self.difficulty = difficulty
        self.behaviors = {
            "aggressive": ["attack", "power_attack", "taunt"],
            "defensive": ["block", "counter", "heal"],
            "tactical":  ["assess", "flank", "exploit_weakness"]
        }

    # Decide which action the enemy should take this turn
    def decide_action(self, combat_state: Dict) -> str:
        # Compose an instruction for the language model
        prompt = f"""As a {self.difficulty} combat AI, choose the best action from {self.behaviors}.

Current state:
- Player HP: {combat_state['player_hp']}/{combat_state['player_max_hp']}
- Enemy  HP: {combat_state['enemy_hp']}/{combat_state['enemy_max_hp']}
- Enemy type: {combat_state['enemy_type']}
- Available actions: {combat_state['available_actions']}

Respond ONLY with one action from the list above."""
        try:
            # Ask the LLM for its choice
            llm_reply = generate_structured_response(prompt)
            # Verify reply is legal; if not, fix it
            return self._validate_action(llm_reply, combat_state['available_actions'])
        except Exception:
            # If the call fails, fall back to rule‑based logic
            return self._fallback_action(combat_state)

    # Check that the model’s answer is among allowed actions
    def _validate_action(self, response: str, valid_actions: List[str]) -> str:
        action = response.strip().lower()
        return action if action in valid_actions else random.choice(valid_actions)

    # Simple backup logic if the LLM doesn’t respond or returns junk
    def _fallback_action(self, combat_state: Dict) -> str:
        # Flee/defend if enemy HP is below 30 %, otherwise random action
        if combat_state['enemy_hp'] < 0.3 * combat_state['enemy_max_hp']:
            return "flee" if "flee" in combat_state['available_actions'] else "defend"
        return random.choice(combat_state['available_actions'])