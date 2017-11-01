import numpy as np
import random

from error import NotEnoughPlayersError
from items import Cards, AutomatedPlayers
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
		self.pot = list()
		self.all_in = list()

		if players < 2:
			raise NotEnoughPlayersError
		else:
			self.players = {x: AutomatedPlayers(starting_amount) for x in range(players)}

	def __str__(self):
		return "game with %i remaining players" % self._check_remaining_players()

	def _play_order(self):
		seats = list(x for x in self.players.keys() if self.players[x].alive)
		return [x for x in seats if x > self.dealer_location] + [x for x in seats if x <= self.dealer_location]

	def _check_remaining_players(self):
		return list(x for x in self.players.keys() if self.players[x].alive)

	def winnings(self, player_seat, amount):
		for player in self._check_remaining_players():
			if player in player_seat:
				self.players[player].reset(amount)
			else:
				self.players[player].reset(0)

	def preflop(self):
		current_players = self._play_order()
		dealt_cards = self.cards.deal_preflop(len(players))
		betting = [0] * len(players)
		current_order = 2

		for player in range(len(current_players)):
			self.players[current_players[player]].deal_cards(dealt_cards[player])
			self.pot += self.players[current_players[player]].ante(self.ante)

			if player < 2:
				betting[player] = self.players[current_players[player]].bet(self.blinds[player])
			else:
				betting[player] += self.players[current_players[player]].best_action(self.pot, self.blinds[player])

		






		





