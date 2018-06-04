
class Transaction(object):
    """A transaction"""
    def __init__(self, sender: str, recipient: str, amount: float):
        self.sender = None
        self.recipient = None
        self.amount = None