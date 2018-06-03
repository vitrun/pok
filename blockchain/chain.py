
class Chain(object):
    """The chain"""
    def __init__(self):
        self.blocks = []

    def new_transaction(self, sender, recipient, amount):
        """
        A new transaction to be included in next block
        :param sender: <str> address of sender
        :param recipient: <str> address of recipient
        :param amount: <float> amount
        :return: <int> the containing block index
        """
        pass