import random
from error import BetTooSmallError, BetTooLargeError
from hand_eval import PlayerEvaluator

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
		all results are returned as (betting amount, is_all_in)
	'''

	def __init__(self, holdings):
		self.cards = None
		self.holdings = holdings
		self.alive = True
		self.in_hand = True

	def deal_cards(self, cards):
		self.cards = list(cards)

	def bet(self, amount, min_bet):
		if (amount > 0) & (amount < min_bet) :
			raise BetTooSmallError
		elif amount > self.holdings:
			raise BetTooLargeError
		else:
			self.holdings -= amount
			return amount, self.holdings == 0

	def ante(self, amount):
		ante_amount = min(self.holdings, amount)
		self.holdings -= ante_amount
		return ante_amount, self.holdings == 0

	def fold(self):
		self.in_hand = False
		return -1, False

	def reset(self, earnings):
		self.holdings += earnings
		if self.holdings == 0:
			self.alive = False
		else:
			self.cards = None
			self.in_hand = True

class AutomatedPlayers(Players):
	'''
	algo driven players
	'''
	def __init__(self, holdings):
		super(AutomatedPlayers, self).__init__(holdings)
		self.probs = 0.5
		self.evaluator = PlayerEvaluator()

	def best_action(self, pot, min_bet):
		if random.random() > self.probs:
			self.bet(min_bet, min_bet)
		else:
			self.fold()









