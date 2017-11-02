import numpy as np
import random

from error import NotEnoughPlayersError
from items import Cards, AutomatedPlayers
from hand_eval import Evaluator
from scipy.stats import rankdata

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
		self.current_players = self._play_order()

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

	def _return_bet_consequences(self, player, community_cards, pot, amount, min_call, min_raise, max_raise):
		bet, allin_player = player.best_action(pot, amount, min_call, min_raise, max_raise)

		if bet > 0:
			est_min_call, est_min_raise = bet, 2 * bet - min_call

		if est_min_call == min_call:
			return max(0, bet), allin_player, min_call, min_raise
		else:
			return bet, allin_player, est_min_call, est_min_raise

	def post_betting(self):
		still_in = list(self.current_players[player] for player in range(len(self.current_players)) if self.players[self.current_players[player]].in_hand)
		card_results = list(self.evaluator.best_hand(self.community_cards + self.players[player].cards) for player in still_in)
		card_list = {self.cards.card_values[x] : x for x in range(len(self.cards.card_values))}
		organized_results = np.array(list([x[1]] + list(card_list[y.card_value] for y in x[0]) for x in card_results))
		single_results = sum(organized_results.T[i] * 50**(organized_results.T.shape[0] - i) for i in range(organized_results.T.shape[0]))
		payouts = [0] * len(self.current_players)

		while sum(self.pot) > 0:
			player_ranking = np.flip(rankdata(single_results).argsort(), 0)
			counter = 0

			while single_results[player_ranking[counter]] == single_results[player_ranking[counter + 1]]:
				counter += 1

			if any(list(player_ranking[x] in self.all_in for x in range(counter + 1))):
				return None
			else:





		for contenders in still_in:



		for player in self._check_remaining_players():
			if player in player_seat:
				self.players[player].reset(amount)
			else:
				self.players[player].reset(0)

	def preflop(self):
		dealt_cards = self.cards.deal_preflop(len(self.current_players))
		betting = [0] * len(self.current_players)
		allin_checker = [False] * len(self.current_players)
		min_call, min_raise = self.blinds[1], self.blinds[1] * 2 - self.blinds[0]
		max_raise = max(x.holdings for x in self.players)

		# ante
		for player in range(len(self.current_players)):
			self.players[self.current_players[player]].deal_cards(dealt_cards[player])
			betting[player], allin_checker[player] = self.players[self.current_players[player]].ante(self.ante)

		# small / big blind
		for player in self.current_players[:2]:
			if allin_checker[x] == False:
				betting[player], allin_checker[player] = self.players[self.current_players[player]].bet(self.blinds[player], min_call, min_raise, max_raise - betting[player])
		
		# betting sequence
		while all(list(betting[x] == max(betting) for x in range(len(self.current_players)) 
					if (allin_checker[x] == False) &
					self.players[self.current_players[x]].in_hand)):
			
			player = (player + 1) % len(self.current_players)
			if (self.current_players[player].in_hand) & (allin_checker[player] == False):
				betting[player], allin_checker[player], min_call, min_raise = self._return_bet_consequences(
						self.players[self.current_players[player]],
						self.community_cards,
						sum(self.pot),
						self.blinds[player],
						min_call,
						min_raise,
						max_raise + self.ante - betting[player])

		# organizing situation
		if sum(allin_checker) == 0:
			self.pot.append(sum(betting))
		else:
			allin_bet_amounts = sorted(list(betting[x] for x in range(len(betting)) if allin_checker[x]))

			for i in range(len(allin_bet_amounts)):
				self.all_in.extend(list(self.current_players[x] for x in range(len(self.current_players)) if betting[x] == allin_bet_amounts[i]))
				
				total_bet_amount = sum(list(min(betting[x], allin_bet_amounts[i]) for x in range(len(self.current_players))))
				self.pot.append(total_bet_amount)

				allin_bet_amounts = list(max(0, x - total_bet_amount) for x in allin_bet_amounts)
				betting = list(max(0, x - total_bet_amount) for x in betting)

			self.pot.append(sum(betting))

	def postflop(self, num_cards):
		self.community_cards.extend(self.cards.deal_postflop(num_cards))
		min_call, min_raise = 0, blinds[1]
		max_raise = max(x.holdings for x in self.players)
		betting = [0] * len(self.current_players)
		allin_checker = [False] * len(self.current_players)

		# first round of betting
		for player in range(len(self.current_players)):
			if (self.current_players[player].in_hand) & (allin_checker[player] == False) & (player not in self.all_in):
				betting[player], allin_checker[player], min_call, min_raise = self._return_bet_consequences(
					self.players[self.current_players[player]],
					self.community_cards,
					sum(self.pot),
					self.blinds[player],
					min_call,
					min_raise,
					max_raise + self.ante - betting[player])

		# until betting is done
		while all(list(betting[x] == max(betting) for x in range(len(self.current_players)) 
					if (allin_checker[x] == False) &
					self.players[self.current_players[x]].in_hand)):

			player = (player + 1) % len(self.current_players)

			if (self.current_players[player].in_hand) & (allin_checker[player] == False) & (player not in self.all_in):
				betting[player], allin_checker[player], min_call, min_raise = self._return_bet_consequences(
					self.players[self.current_players[player]],
					self.community_cards,
					sum(self.pot),
					self.blinds[player],
					min_call,
					min_raise,
					max_raise + self.ante - betting[player])					

		# organizing bets
		if sum(allin_checker) == len(self.all_in):
			self.pot[-1] += sum(betting)
		else:
			allin_bet_amounts = sorted(list(betting[x] for x in range(len(betting)) if allin_checker[x]))

			for i in range(len(allin_bet_amounts)):
				self.all_in.extend(list(self.current_players[x] for x in range(len(self.current_players)) if betting[x] == allin_bet_amounts[i]))
				
				total_bet_amount = sum(list(min(betting[x], allin_bet_amounts[i]) for x in range(len(self.current_players))))
				self.pot[-1] += total_bet_amount
				self.pot.append(0)

				allin_bet_amounts = list(max(0, x - total_bet_amount) for x in allin_bet_amounts)
				betting = list(max(0, x - total_bet_amount) for x in betting)

			self.pot[-1] += sum(betting)
