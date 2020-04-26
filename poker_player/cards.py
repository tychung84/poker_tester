from typing import Dict, List
import random

from .constants import SUITS, VALUES


class Card(object):
    """A single card object.
    """

    def __init__(self, suit: str, card_value: str):
        """
        Creates a card
        :param suit: a str character indicating the suit of the card.
        :param card_value: a str character indicating the value of the card.
        """
        assert (suit in SUITS)
        assert (card_value in VALUES)
        self.suit = suit
        self.card_value = card_value

    def __str__(self):
        return self.card_value + self.suit


class Dealer(object):
    """deals with the mechanics of how the cards are dealt
    """

    def __init__(self):
        self.suits = SUITS
        self.card_values = VALUES
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
        return 'deck with %i cards left' % (52 - self.counter)

    def shuffle(self) -> None:
        """
            Shuffles the cards.
        """
        self.counter = 0
        random.shuffle(self.cards)

    def deal_players(self, players: int) -> Dict[int, List[Card]]:
        """
        Deals cards to the players. Note that the cards are dealt a card a piece by player (and not two consecutive
        cards to any player).
        :param players: number of players in the hand.
        :return: a dictionary mapping the players with their hands.
        """
        cards_dealt = [next(self) for x in range(players * 2)]
        return {x: [cards_dealt[x], cards_dealt[x + players]] for x in range(players)}

    def deal_common(self, num_cards: int) -> List[Card]:
        """
        Deals cards to the common deck. Note that every time a card is dealt this way, the first card is burnt.
        :param num_cards: number of cards to deal.
        :return: a List of Card values.
        """
        cards_dealt = [next(self) for x in range(num_cards + 1)]
        return cards_dealt[1:]
