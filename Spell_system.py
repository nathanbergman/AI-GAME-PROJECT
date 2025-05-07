from character import Character, Player
class SpellSystem:
	def __init__(self, playerObj):
		self.player = playerObj
	def cast_spell( self, spellName):
		spellName = spellName.lower()
		if self.player.max_mana == 0:
			print("\n It seems as you have no connection to the arcane. You cannot cast spells.")
			return
		elif self.player.mana <= 0:
			print("\n It seems as you are out of mana. Try resting to get more.")
			return


		if spellName == "ice":
			mana_cost = 5
			self.player.mana -= mana_cost
			#spell Effect
			self.player.base_defense += 2
			self.player.floatingD += 2
			print("\n You surround your body with Ice, blocking damage")
		elif spellName == "fire":
			mana_cost = 5
			self.player.mana -= mana_cost
			#spell Effect
			self.player.base_attack += 1
			self.player.floatingA += 1

			print("\n You surround your hands with fire, dealing more damage")
		elif spellName == "healing":
			mana_cost = 2
			self.player.mana -= mana_cost
			#spell effect 
			self.player.heal(25)
			if self.player.health >= self.player.max_health:
				self.player.health = self.player.max_health
				print("\n You feel completly refreshed from the healing")
			else:
				print("\n You healed yourself")	
		else:	
			print("not a spell")
		if self.player.mana <= 0:
			self.player.mana = 0
		return	 