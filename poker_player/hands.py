from enum import Enum
from typing import Dict, List, Tuple
from .cards import Card
from .constants import VALUES


class HandValues(Enum):
	STRAIGHT_FLUSH = 8
	QUADS = 7
	FULL_HOUSE = 6
	FLUSH = 5
	STRAIGHT = 4
	TRIPS = 3
	TWO_PAIR = 2
	ONE_PAIR = 1
	HIGH_CARD = 0


def _count_values(cards: List[Card]) -> Dict[str, List[Card]]:
	"""
	Creates a dictionary of Cards by card_value for a list of cards.
	:param cards: All valid cards in a List
	:return: mapping of Lists of Cards by card_value
	"""
	return {card_value: list(
		x for x in cards if x.card_value == card_value) for card_value in set(x.card_value for x in cards)}


def _count_suits(cards: List[Card]) -> Dict[str, List[Card]]:
	"""
	Creates a dictionary of Cards by suit for a list of cards.
	:param cards:  All valid cards in a List
	:return: mapping of Lists of Cards by suit
	"""
	return {suit: list(x for x in cards if x.suit == suit) for suit in set(x.suit for x in cards)}


class Evaluator(object):
	def __init__(self):
		self._card_values = VALUES
		self._value_ranking = {self._card_values[x]: x for x in range(len(self._card_values))}

	def return_pairs(self, cards: List[Card]) -> List[List[Card]]:
		"""
		Returns all combinations of pairs.
		:param cards: All cards in a hand
		:return: List of pairs (in a List)
		"""
		card_values = _count_values(cards)
		pairs = sorted(
			[x for x in card_values.keys() if len(card_values[x]) == 2], key=lambda x: self._value_ranking[x])
		return [card_values[x] for x in pairs]

	def return_trips(self, cards: List[Card]) -> List[List[Card]]:
		"""
		Returns all combinations of trips.
		:param cards: All cards in a hand
		:return: List of trips (in a List)
		"""
		card_values = _count_values(cards)
		trips = sorted(
			[x for x in card_values.keys() if len(card_values[x]) == 3], key=lambda x: self._value_ranking[x])
		return [card_values[x] for x in trips]

	def return_quads(self, cards: List[Card]) -> List[List[Card]]:
		"""
		Returns all combinations of quads.
		:param cards: All cards in a hand
		:return: List of quads (in a List)
		"""
		card_values = _count_values(cards)
		quads = sorted(
			[x for x in card_values.keys() if len(card_values[x]) == 4], key=lambda x: self._value_ranking[x])
		return [card_values[x] for x in quads]

	def return_full_house(self, cards: List[Card]) -> List[Card]:
		"""
		Returns a list of Cards containing a full house if there is one; an empty list otherwise.
		:param cards: All cards in a hand
		:return: List of cards indicating a full house.
		"""
		pairs, trips = self.return_pairs(cards), self.return_trips(cards)

		if (len(trips + pairs) < 2) | (len(trips) == 0):
			return list()
		elif len(trips) == 2:
			return trips[-1] + trips[-2][:2]
		else:
			return trips[-1] + pairs[-1]

	def return_straights(self, cards: List[Card]) -> List[Card]:
		"""
		Returns the highest straight given a list of cards.
		:param cards: All cards in a hand
		:return: The largest straight, if there is one. Empty list otherwise.
		"""
		card_values = _count_values(cards)
		unique_card_values = ''.join(sorted(list(set(card_values)), key=lambda x: self._value_ranking[x]))
		straight_possibilities = 'A' + self._card_values
		straights = [
			straight_possibilities[x: x+5] for x in range(
				len(straight_possibilities) - 4) if straight_possibilities[x: x+5] in unique_card_values]

		if straights == list():
			return list()
		else:
			return list(card_values[x][0] for x in straights[-1])

	def return_flushes(self, cards: List[Card]) -> List[Card]:
		"""
		Returns all cards that fit a flush given a hand.
		:param cards: All cards in a hand
		:return: The largest flush, if there is one. Empty list otherwise.
		"""
		suits = _count_suits(cards)
		flushes = [x for x in suits.keys() if len(suits[x]) >= 5]

		if flushes == list():
			return list()
		else:
			return sorted(suits[flushes[0]], key=lambda x: self._value_ranking[x.card_value])

	def return_high_card(self, cards: List[Card], number: int) -> List[Card]:
		"""
		Returns the highest list of n cards given a hand
		:param cards: number of cards to return.
		:param number: Size of the list to return
		:return: A list of largest hands.
		"""
		return sorted([x for x in cards], key=lambda x: self._value_ranking[x.card_value], reverse=True)[:number]

	def best_hand(self, cards: List[Card]) -> Tuple[List[Card], HandValues]:
		"""
		Returns the best hand given a set of cards.
		:param cards: List of given cards
		:return: a Tuple of the best possible hand and an enum for the HandValues.
		"""
		if len(self.return_straights(self.return_flushes(cards))):
			return self.return_straights(self.return_flushes(cards)), HandValues.STRAIGHT_FLUSH
		elif len(self.return_quads(cards)):
			quads = self.return_quads(cards)
			return quads[-1] + self.return_high_card(list(set(cards) - set(quads[-1])), 1), HandValues.QUADS
		elif len(self.return_full_house(cards)):
			return self.return_full_house(cards), HandValues.FULL_HOUSE
		elif len(self.return_flushes(cards)):
			return self.return_flushes(cards)[-5:], HandValues.FLUSH
		elif len(self.return_straights(cards)):
			return self.return_straights(cards), HandValues.STRAIGHT
		elif len(self.return_trips(cards)):
			trips = self.return_trips(cards)
			return trips[-1] + self.return_high_card(list(set(cards) - set(trips[-1])), 2), HandValues.TRIPS
		elif len(self.return_pairs(cards)):
			pairs = self.return_pairs(cards)
			if len(pairs) > 1:
				two_pairs = pairs[-1] + pairs[-2]
				return two_pairs + self.return_high_card(list(set(cards) - set(two_pairs)), 1), HandValues.TWO_PAIR
			else:
				return pairs[-1] + self.return_high_card(list(set(cards) - set(pairs[-1])), 3), HandValues.ONE_PAIR
		else:
			return self.return_high_card(cards, 5), HandValues.HIGH_CARD


class PlayerEvaluator(Evaluator):
	def __init__(self):
		super(PlayerEvaluator, self).__init__()
