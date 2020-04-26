import unittest
from .cards import Card
from .hands import Evaluator, HandValues


def _generate_hands(card_value: str) -> Card:
	"""
	Generates a card given a string input.
	:param card_value: string input, with value first (i.e. AH)
	:return: The appropriate card
	"""
	return Card(card_value[1], card_value[0])


class TestHands(unittest.TestCase):
	def test_pairs(self):
		evaluator = Evaluator()
		# one pair.
		card_values = ['2H', '3D', '2S', '4C', '5C', 'JH', 'AH']
		cards = {x: _generate_hands(x) for x in card_values}
		self.assertEqual(evaluator.return_pairs([cards[x] for x in cards.keys()]), [[cards['2H'], cards['2S']]])

		# trips
		card_values = ['2H', '3D', '2S', '4C', '5C', '2C', 'AH']
		cards = {x: _generate_hands(x) for x in card_values}
		self.assertEqual(evaluator.return_pairs([cards[x] for x in cards.keys()]), list())

		# two pair
		card_values = ['2H', '3D', '2S', '4C', '5C', 'JH', 'JC']
		cards = {x: _generate_hands (x) for x in card_values}
		self.assertEqual(evaluator.return_pairs ([cards[x] for x in cards.keys ()]),
		                 [[cards['2H'], cards['2S']], [cards['JH'], cards['JC']]])

		# three pair
		card_values = ['2H', '3D', '2S', '5S', '5C', 'JH', 'JC']
		cards = {x: _generate_hands (x) for x in card_values}
		self.assertEqual(evaluator.return_pairs ([cards[x] for x in cards.keys ()]),
		                 [[cards['2H'], cards['2S']], [cards['5S'], cards['5C']], [cards['JH'], cards['JC']]])

	def test_trips(self):
		evaluator = Evaluator()
		# no trips
		card_values = ['2H', '3D', '2S', '4C', '5C', '6C', 'AH']
		cards = {x: _generate_hands(x) for x in card_values}
		self.assertEqual(evaluator.return_trips([cards[x] for x in cards.keys()]), list())

		# one trips
		card_values = ['2H', '3D', '2S', '4C', '5C', '2C', 'AH']
		cards = {x: _generate_hands(x) for x in card_values}
		self.assertEqual(evaluator.return_trips([cards[x] for x in cards.keys()]),
		                 [[cards['2H'], cards['2S'], cards['2C']]])


		# two trips
		card_values = ['2H', '3D', '2S', '3C', '5C', '2C', '3H']
		cards = {x: _generate_hands (x) for x in card_values}
		self.assertEqual(evaluator.return_trips([cards[x] for x in cards.keys()]),
		                 [[cards['2H'], cards['2S'], cards['2C']], [cards['3D'], cards['3C'], cards['3H']]])

	def test_quads(self):
		evaluator = Evaluator()
		# no quads
		card_values = ['2H', '3D', '2S', '4C', '5C', '6C', '2C']
		cards = {x: _generate_hands(x) for x in card_values}
		self.assertEqual(evaluator.return_quads([cards[x] for x in cards.keys()]), list())

		# one quad
		card_values = ['2H', '2D', '2S', '4C', '5C', '2C', 'AH']
		cards = {x: _generate_hands(x) for x in card_values}
		self.assertEqual(evaluator.return_quads([cards[x] for x in cards.keys()]),
		                 [[cards['2H'], cards['2D'], cards['2S'], cards['2C']]])


		# two quads
		card_values = ['2H', '2D', '2S', '3C', '3H', '2C', '3D', '3S']
		cards = {x: _generate_hands (x) for x in card_values}
		self.assertEqual(evaluator.return_quads([cards[x] for x in cards.keys()]),
		                 [[cards['2H'], cards['2D'], cards['2S'], cards['2C']],
		                  [cards['3C'], cards['3H'], cards['3D'], cards['3S']]])

	def test_full_houses(self):
		evaluator = Evaluator()
		# no house
		card_values = ['2H', '3D', '2S', '4C', '5C', '6C', '2C']
		cards = {x: _generate_hands(x) for x in card_values}
		self.assertEqual(evaluator.return_full_house([cards[x] for x in cards.keys()]), list())

		# one trip + one pair
		card_values = ['2H', '3D', '2S', '4C', '5C', '3C', '2C']
		cards = {x: _generate_hands (x) for x in card_values}
		results = set(cards[x] for x in ['2H', '3D', '2S', '3C', '2C'])
		self.assertEqual(set(evaluator.return_full_house([cards[x] for x in cards.keys()])), results)

		# one trip + two pair
		card_values = ['2H', '3D', '2S', '4C', '4D', '3C', '2C']
		cards = {x: _generate_hands(x) for x in card_values}
		results = set(cards[x] for x in ['2H', '4D', '2S', '4C', '2C'])
		self.assertEqual(set(evaluator.return_full_house([cards[x] for x in cards.keys()])), results)

		# two trips
		card_values = ['2H', '3D', '2S', '3C', '5C', '3S', '2C']
		cards = {x: _generate_hands(x) for x in card_values}
		results = evaluator.return_full_house([cards[x] for x in cards.keys()])
		self.assertEqual(len([x for x in results if x.card_value == '3']), 3)
		self.assertEqual(len([x for x in results if x.card_value == '2']), 2)

		# quads + pair
		card_values = ['2H', '2D', '2S', '2C', '5C', '6C', '6D']
		cards = {x: _generate_hands(x) for x in card_values}
		self.assertEqual(evaluator.return_full_house([cards[x] for x in cards.keys()]), list())

	def test_straight(self):
		evaluator = Evaluator()
		# no straight
		card_values = ['2H', '3D', '2S', '4C', '5C', '5D', '2C']
		cards = {x: _generate_hands(x) for x in card_values}
		self.assertEqual(evaluator.return_straights([cards[x] for x in cards.keys()]), list())

		# one straight
		card_values = ['2H', '3D', 'KS', '4C', '5C', '6D', 'JC']
		cards = {x: _generate_hands(x) for x in card_values}
		results = list(cards[x] for x in ['2H', '3D', '4C', '5C', '6D'])
		self.assertEqual(evaluator.return_straights([cards[x] for x in cards.keys()]), results)

		# multiple straights
		card_values = ['2H', '3D', 'AS', '4C', '5C', '6D', 'JC']
		cards = {x: _generate_hands(x) for x in card_values}
		results = list(cards[x] for x in ['2H', '3D', '4C', '5C', '6D'])
		self.assertEqual(evaluator.return_straights([cards[x] for x in cards.keys()]), results)

	def test_flush(self):
		evaluator = Evaluator()
		# no flush
		card_values = ['2H', '3D', '2S', '4C', '5C', '5D', '2C']
		cards = {x: _generate_hands (x) for x in card_values}
		self.assertEqual(evaluator.return_flushes([cards[x] for x in cards.keys ()]), list())

		# one flush
		card_values = ['2H', '3H', '2S', '4H', '5H', '5D', '7H']
		cards = {x: _generate_hands (x) for x in card_values}
		results = list(cards[x] for x in ['2H', '3H', '4H', '5H', '7H'])
		self.assertEqual(evaluator.return_flushes([cards[x] for x in cards.keys ()]), results)

		# multiple flushes
		card_values = ['2H', '3H', '4H', '8H', 'TH', 'AH', 'KH']
		cards = {x: _generate_hands(x) for x in card_values}
		results = list(cards[x] for x in ['2H', '3H', '4H', '8H', 'TH', 'KH', 'AH'])
		self.assertEqual(evaluator.return_flushes([cards[x] for x in cards.keys()]), results)

	def test_straight_flush(self):
		evaluator = Evaluator()
		# straight and flush but no straight flush
		card_values = ['2H', '3H', '4H', '5H', '6C', '7C', '8C']
		cards = {x: _generate_hands(x) for x in card_values}
		_, hand_type = evaluator.best_hand([cards[x] for x in cards.keys()])
		self.assertNotEqual(hand_type, HandValues.STRAIGHT_FLUSH)

		# one straight flush
		card_values = ['2H', '3H', '4H', '5H', '6H', '7C', '8C']
		cards = {x: _generate_hands(x) for x in card_values}
		results = list(cards[x] for x in ['2H', '3H', '4H', '5H', '6H'])
		predicted_best_hand, hand_type = evaluator.best_hand([cards[x] for x in cards.keys()])
		self.assertEqual(predicted_best_hand, results)
		self.assertEqual(hand_type, HandValues.STRAIGHT_FLUSH)

		# multiple straight flushes
		card_values = ['2H', '3H', '4H', '5H', '6H', '7H', '8H']
		cards = {x: _generate_hands(x) for x in card_values}
		results = list(cards[x] for x in ['4H', '5H', '6H', '7H', '8H'])
		predicted_best_hand, hand_type = evaluator.best_hand([cards[x] for x in cards.keys()])
		self.assertEqual(predicted_best_hand, results)
		self.assertEqual(hand_type, HandValues.STRAIGHT_FLUSH)


if __name__ == '__main__':
	unittest.main()
