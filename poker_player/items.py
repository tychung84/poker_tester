import random
from error import BetTooSmallError, BetTooLargeError

class Card(object):
	
	'''card object
	'''

	def __init__(self, suit, card_value):
		self.suit = suit
		self.card_value = card_value

	def __str__(self):
		return self.card_value + self.suit

class Cards(object):
	
	'''deals with the mechanics of how the cards are dealt
	'''

	def __init__(self):
		self.suits = 'DHCS'
		self.card_values = '23456789TJQKA'
		self.cards = [Card(x, y) for x in self.suits for y in self.card_values]
		self.counter = 0
		self.shuffle()

	def __iter__(self):
		return self

	def __next__(self):
		if self.counter >= 52:
			raise StopIteration
		else:
			self.counter += 1
			return self.cards[self.counter - 1]

	def __str__(self):
		return ('deck with %i cards left' % (52 - self.counter))
		
	def shuffle(self):
		self.counter = 0
		random.shuffle(self.cards)

	def deal_preflop(self, players):
		cards_dealt = [next(self) for x in range(players * 2)]
		return {x: [cards_dealt[x], cards_dealt[x + players]] for x in range(players)}

	def deal_postflop(self, num_cards):
		cards_dealt = [next(self) for x in range(num_cards)]
		return cards_dealt[1:]

class Players(object):

	''' deals with the player holdings and results
	'''

	def __init__(self, holdings):
		self.cards = list()
		self.holdings = holdings
		self.alive = True
		self.in_hand = True

	def deal_cards(self, cards):
		self.cards = cards

	def bet(self, amount, bet_increase):
		if (amount > 0) & (amount < bet_increase) & (self.holdings >= bet_increase):
			raise BetTooSmallError
		elif amount > self.holdings:
			raise BetTooLargeError
		else:
			self.holdings -= amount

	def fold(self):
		self.in_hand = False

	def reset(self, earnings):
		self.holdings += earnings
		if self.holdings == 0:
			self.alive = False
		else:
			self.cards = list()
			self.in_hand = True





