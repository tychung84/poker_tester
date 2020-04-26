class Error (Exception):
    pass


class NotEnoughPlayersError (Error):
    """ when too many cards have been drawn
    """

    def __init__(self, message):
        self.message = "must have more than one player!"


class BetTooSmallError (Error):
    """ too little has been bet
    """

    def __init__(self, message):
        self.message = "you must bet at least as much as the prior bet increase!"


class BetTooLargeError (Error):
    """ when the bet is larger than holdings
    """

    def __init__(self, message):
        self.message = "you have bet more than what you have!"
