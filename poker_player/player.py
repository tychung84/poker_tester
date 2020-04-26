from .error import BetTooLargeError, BetTooSmallError


class Players(object):
    """ deals with the player holdings and results
    all results are returned as (betting amount, is_all_in)
    """

    def __init__(self, holdings):
        self.cards = None
        self.holdings = holdings
        self.alive = True
        self.in_hand = True
        self.min_bet = 0
        self.min_raise = 0

    def deal_cards(self, cards):
        self.cards = list(cards)

    def bet(self, amount, min_bet, min_raise):
        self.min_bet = min_bet
        self.min_raise = min_raise

        if amount == self.holdings:
            self.holdings -= amount
            return amount, self.holdings == 0
        elif amount > self.holdings:
            raise BetTooLargeError
        else:
            if (amount < min_bet) | ((amount > min_bet) & (amount < min_raise)):
                raise BetTooSmallError
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
