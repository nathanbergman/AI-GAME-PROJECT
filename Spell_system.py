from character import Character, Player
class SpellSystem:
	def __init__(self, playerObj):
		self.player = playerObj
	def cast_spell( self, spellName):
		if spellName == "fireball":
			print("fireball casted")
			return true
		elif spellName == "healing":
			print("healing catsed")
			return true
		else:	
			print("not a spell")
			return false