import unittest
from .cards import Card, Dealer


class TestCard(unittest.TestCase):
	def test_card_creation(self):
		test_card = Card('C', '2')
		self.assertEqual(str(test_card), '2C')
		with self.assertRaises(AssertionError):
			Card('A', '2')
		with self.assertRaises(AssertionError):
			Card('C', '1')

	def test_dealers_cards(self):
		dealer = Dealer()
		self.assertEqual(len(dealer.cards), 52)

		unique_card = set()
		for card in dealer.cards:
			unique_card.add(str(card))
		self.assertEqual(len(unique_card), 52)

	def test_total_counts(self):
		dealer = Dealer()
		_ = dealer.deal_common(50)  # accounts for the burnt card
		with self.assertRaises(StopIteration):
			_ = dealer.deal_common(1)

	def test_player_deal(self):
		dealer = Dealer()
		total_players = 9
		dealt_cards = dealer.deal_players(total_players)
		for i in range(len(dealer.cards)):
			for j in range(total_players):
				if dealt_cards[j][0] == dealer.cards[i]:
					self.assertNotEqual(dealt_cards[j][1], dealer.cards[i+1])

	def test_community_deal(self):
		dealer = Dealer()
		first_card = dealer.deal_common(1)
		second_card = dealer.deal_common(1)

		for i in range(len(dealer.cards)):
			if first_card == dealer.cards[i]:
				self.assertNotEqual(second_card, dealer.cards[i+1])


if __name__ == '__main__':
	unittest.main()
