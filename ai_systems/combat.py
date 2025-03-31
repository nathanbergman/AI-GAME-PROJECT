from ollama_integration import generate_structured_response
from typing import Dict, List
import random


class TacticalCombatAI:
    def __init__(self, difficulty: str = "normal"):
        self.difficulty = difficulty
        self.behaviors = {
            "aggressive": ["attack", "power_attack", "taunt"],
            "defensive": ["block", "counter", "heal"],
            "tactical": ["assess", "flank", "exploit_weakness"]
        }

    def decide_action(self, combat_state: Dict) -> str:
        prompt = f"""As a {self.difficulty} difficulty combat AI, choose the best action from {self.behaviors}.

Current state:
- Player HP: {combat_state['player_hp']}/{combat_state['player_max_hp']}
- Enemy HP: {combat_state['enemy_hp']}/{combat_state['enemy_max_hp']}
- Enemy type: {combat_state['enemy_type']}
- Available actions: {combat_state['available_actions']}

Respond ONLY with the action key from available actions."""

        try:
            response = generate_structured_response(prompt)
            return self._validate_action(response, combat_state['available_actions'])
        except:
            return self._fallback_action(combat_state)

    def _validate_action(self, response: str, valid_actions: List[str]) -> str:
        action = response.strip().lower()
        return action if action in valid_actions else random.choice(valid_actions)

    def _fallback_action(self, combat_state: Dict) -> str:
        if combat_state['enemy_hp'] < 0.3 * combat_state['enemy_max_hp']:
            return "flee" if "flee" in combat_state['available_actions'] else "defend"
        return random.choice(combat_state['available_actions'])