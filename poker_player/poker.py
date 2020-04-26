import numpy as np
import random

from scipy.stats import rankdata

from .error import NotEnoughPlayersError
from .cards import Dealer
from .hands import Evaluator

class GameState(object):
	"""State of individual poker match
	"""

	def __init__(self, blinds=(1, 2), starting_amount=100, players=2, ante=0):
		self.blinds = blinds
		self.ante = ante
		self.cards = Dealer()
		self.dealer_location = random.choice(range(players))
		self.evaluator = Evaluator()

		if players < 2:
			raise NotEnoughPlayersError
		else:
			self.players = {x: AutomatedPlayers(starting_amount) for x in range(players)}

		self._reset_game()

	def __str__(self):
		return "game with %i remaining players" % self._check_remaining_players()

	def _play_order(self):
		seats = list(x for x in self.players.keys() if self.players[x].alive)
		return [x for x in seats if x > self.dealer_location] + [x for x in seats if x <= self.dealer_location]

	def _check_remaining_players(self):
		return list(x for x in self.players.keys() if self.players[x].alive)

	def _return_bet_consequences(self, player, pot, min_call, min_raise, max_raise):
		bet, allin_player = player.best_action(pot, self.community_cards, min_call, min_raise, max_raise)
		return max(0, bet), allin_player

	def _find_next_dealer(self):
		self.dealer_location = (self.dealer_location + 1) % len(self.players.keys())

		while not self.players[self.dealer_location].alive:
			self.dealer_location = (self.dealer_location + 1) % len(self.players.keys())

	def _reset_game(self):
		# resetting game
		self.cards.shuffle()
		self.pot = [0]
		self.all_in = list()
		self.community_cards = list()
		self._find_next_dealer()
		self.current_players = self._play_order()

	def _still_in(self):
		return sum(list(self.players[x].in_hand for x in self.players.keys()))

	def _betting_sequence(self, current_turn, betting, allin_checker, min_call, min_raise):
		max_raise = max(self.players[self.current_players[x]].holdings for x in range(len(self.current_players)))
		countdown = self._still_in()

		while (all(list(betting[x] == max(betting) for x in range(len(self.current_players)) if (allin_checker[x] == False) & self.players[self.current_players[x]].in_hand)) == False) | (countdown > 0):
			if self._still_in() <= 1:
				break 			
			elif self.players[self.current_players[current_turn]].in_hand & (allin_checker[current_turn] == False):
				this_bet, allin_checker[current_turn] = self._return_bet_consequences(
						self.players[self.current_players[current_turn]],
						sum(self.pot),
						min_call - betting[current_turn],
						min_raise - betting[current_turn],
						max_raise - betting[current_turn])

				new_total = this_bet + betting[current_turn]

				if new_total > min_call:
					min_raise = (2 * new_total) - min_call
					min_call = new_total

				betting[current_turn] += max(0, this_bet)

			current_turn = (current_turn + 1) % len(self.current_players)
			countdown -= 1

		return betting, allin_checker

	def _calculate_bets(self, betting, allin_checker):
		if sum(allin_checker) == len(self.all_in):
			self.pot[-1] += sum(betting)
		elif self._still_in() == 1:
			self.pot[-1] += sum(betting)
			self.post_betting()
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

	def post_betting(self):
		# getting hands and ranking them
		still_in = list(player for player in range(len(self.current_players)) if self.players[self.current_players[player]].in_hand)
		card_results = list(self.evaluator.best_hand(self.community_cards + self.players[self.current_players[player]].cards) for player in range(len(self.current_players)))
		
		# changing hands into single value hands
		# picked 50 since it's larger than any card value or card hand value
		card_list = {self.cards.card_values[x] : x for x in range(len(self.cards.card_values))}
		organized_results = np.array(list([x[1]] + list(card_list[y.card_value] for y in x[0]) for x in card_results))
		single_results = sum(organized_results.T[i] * (50 ** (organized_results.T.shape[0] - i)) for i in range(organized_results.T.shape[0]))
		
		# setting up payouts
		payouts = [0] * len(self.current_players)

		while sum(self.pot) > 0:
			if len(self.all_in) > 0:
				player_in_focus = self.all_in[0]
				better_hands = np.where(single_results[player_in_focus] < single_results)[0]
				equal_hands = np.where(single_results[player_in_focus] == single_results)[0]
				better_hands_still_in = list(x for x in better_hands if x in still_in)
				equal_hands_still_in = list(x for x in equal_hands if x in still_in)

				if any(list(self.players[self.current_players[x]].in_hand for x in better_hands)):
					self.pot[1] += self.pot[0]
				else:
					for player in equal_hands:
						payouts[self.current_players[player]] += self.pot[0] / len(equal_hands_still_in)

				self.pot = self.pot[1:]
				self.all_in = self.all_in[1:]
				still_in.remove(player_in_focus)
			else:
				player_in_focus = still_in[0]
				better_hands = np.where(single_results[player_in_focus] < single_results)[0]
				equal_hands = np.where(single_results[player_in_focus] == single_results)[0]
				better_hands_still_in = list(x for x in better_hands if x in still_in)
				equal_hands_still_in = list(x for x in equal_hands if x in still_in)

				if len(better_hands_still_in) == 0:
					for player in equal_hands_still_in:
						payouts[self.current_players[player]] += self.pot[0] / len(equal_hands_still_in)
					self.pot = self.pot[1:]

				still_in.remove(player_in_focus)

		# distributing payouts
		for player in range(len(self.current_players)):
			self.players[self.current_players[player]].reset(payouts[self.current_players[player]])

		self._reset_game()

	def preflop(self):
		dealt_cards = self.cards.deal_preflop(len(self.current_players))
		betting = [0] * len(self.current_players)
		allin_checker = [False] * len(self.current_players)
		min_call, min_raise = self.blinds[1], self.blinds[1] * 2 - self.blinds[0]
		max_raise = max(self.players[self.current_players[x]].holdings for x in range(len(self.current_players)))

		# ante
		for player in range(len(self.current_players)):
			self.players[self.current_players[player]].deal_cards(dealt_cards[player])
			betting[player], allin_checker[player] = self.players[self.current_players[player]].ante(self.ante)

		# small / big blind
		checker = False
		for player in self.current_players[:2]:
			if not allin_checker[player]:
				betting[player], allin_checker[player] = self.players[self.current_players[player]].bet(self.blinds[checker], self.blinds[checker], min_raise, max_raise - betting[player])
				checker = True
			else:
				betting[player], allin_checker[player] = self.players[self.current_players[player]].bet(self.blinds[checker], self.blinds[checker], min_raise, max_raise - betting[player])

		# betting sequence
		betting, allin_checker = self._betting_sequence(self.current_players[2], betting, allin_checker, min_call, min_raise)
		self._calculate_bets(betting, allin_checker)

	def postflop(self, num_cards):
		self.community_cards.extend(self.cards.deal_postflop(num_cards))
		min_call, min_raise = 0, self.blinds[1]
		max_raise = max(self.players[self.current_players[x]].holdings for x in range(len(self.current_players)))
		betting = [0] * len(self.current_players)
		allin_checker = [False] * len(self.current_players)

		# first round of betting
		betting, allin_checker = self._betting_sequence(self.current_players[0], betting, allin_checker, min_call, min_raise)
		self._calculate_bets(betting, allin_checker)
