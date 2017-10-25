import numpy as np
import random

from error import NotEnoughPlayersError
from items import Cards, Players
from hand_eval import Evaluator

class GameState(object):
	"""State of individual poker match
	"""

	def __init__(self, blinds=(1, 2), starting_amount=100, players=2, ante=0):
		self.blinds = blinds
		self.ante = ante
		self.cards = Cards()
		self.community_cards = list()
		self.dealer_location = random.choice(range(players))
		self.evaluator = Evaluator()

		if players < 2:
			raise NotEnoughPlayersError
		else:
			self.players = [Players(starting_amount) for x in range(players)]

	def preflop(self):





