from enum import Enum


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

	def __setattr__(self, *_):
		pass


def _count_values(cards):
	return {card_value: list(x for x in cards if x.card_value == card_value) for card_value in set(x.card_value for x in cards)}


def _count_suits(cards):
	return {suit: list(x for x in cards if x.suit == suit) for suit in set(x.suit for x in cards)}


class Evaluator(object):
	def __init__(self):
		self._card_values = '23456789TJQKA'
		self._value_ranking = {self._card_values[x]: x for x in range(len(self._card_values))}
		self._hand_values = HandValues()

	def return_pairs(self, cards):
		card_values = _count_values(cards)
		pairs = sorted([x for x in card_values.keys() if len(card_values[x]) == 2], key=lambda x: self._value_ranking[x])
		return [card_values[x] for x in pairs]

	def return_trips(self, cards):
		card_values = _count_values(cards)
		trips = sorted([x for x in card_values.keys() if len(card_values[x]) == 3], key=lambda x: self._value_ranking[x])
		return [card_values[x] for x in trips]

	def return_quads(self, cards):
		card_values = _count_values(cards)
		quads = sorted([x for x in card_values.keys() if len(card_values[x]) == 4], key=lambda x: self._value_ranking[x])
		return [card_values[x] for x in quads]

	def return_full_house(self, cards):
		pairs, trips = self.return_pairs(cards), self.return_trips(cards)

		if (len(trips + pairs) < 2) | (len(trips) == 0):
			return list()
		elif len(trips) == 2:
			return trips[-1] + trips[-2][:2]
		else:
			return trips[-1] + pairs[-1]

	def return_straights(self, cards):
		card_values = _count_values(cards)
		unique_card_values = ''.join(sorted(list(set(card_values)), key=lambda x: self._value_ranking[x]))
		straight_possibilities = 'A' + self._card_values
		straights = [straight_possibilities[x: x+5] for x in range(len(straight_possibilities) - 4) if straight_possibilities[x: x+5] in unique_card_values]

		if straights == list():
			return list()
		else:
			return list(card_values[x][0] for x in straights[-1])

	def return_flushes(self, cards):
		suits = _count_suits(cards)
		flushes = [x for x in suits.keys() if len(suits[x]) >= 5]

		if flushes == list():
			return list()
		else:
			return sorted(suits[flushes[0]], key=lambda x: self._value_ranking[x.card_value])

	def return_high_card(self, cards, number):
		return sorted([x for x in cards], key=lambda x: self._value_ranking[x.card_value], reverse=True)[:number]

	def best_hand(self, cards):
		flushes, straights = self.return_flushes(cards), self.return_straights(cards)
		pairs, trips, quads, full_house = self.return_pairs(cards), self.return_trips(cards), self.return_quads(cards), self.return_full_house(cards)
		straight_flush = self.return_straights(self.return_flushes(cards))

		if len(straight_flush) > 0:
			return straight_flush, self._hand_values.STRAIGHT_FLUSH
		elif len(quads) > 0:
			return quads[-1] + self.return_high_card(list(set(cards) - set(quads[-1])), 1), self._hand_values.QUADS
		elif len(full_house) > 0:
			return full_house, self._hand_values.FULL_HOUSE
		elif len(flushes) > 0:
			return flushes[-5:], self._hand_values.FLUSH
		elif len(straights) > 0:
			return straights, self._hand_values.STRAIGHT
		elif len(trips) > 0:
			return trips[-1] + self.return_high_card(list(set(cards) - set(trips[-1])), 2) , self._hand_values.TRIPS
		elif len(pairs) > 1:
			two_pairs = pairs[-1] + pairs[-2]
			return two_pairs + self.return_high_card(list(set(cards) - set(two_pairs)), 1), self._hand_values.TWO_PAIR
		elif len(pairs) > 0:
			return pairs[-1] + self.return_high_card(list(set(cards) - set(pairs[-1])), 3) , self._hand_values.ONE_PAIR
		else:
			return self.return_high_card(cards, 5), self._hand_values.HIGH_CARD


class PlayerEvaluator(Evaluator):
	def __init__(self):
		super(PlayerEvaluator, self).__init__()
