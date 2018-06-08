
class Chain(object):
    """The chain"""
    def __init__(self):
        self.blocks = []
        self.current_transactions = []

    @property
    def last_block(self):
        return self.blocks[-1] if self.blocks else None
