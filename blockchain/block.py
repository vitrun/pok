
class Block(object):
    """The block structure"""
    def __init__(self):
        self.index = None
        self.timestamp = None
        self.proof = None
        self.prev_hash = None
        self.transactions = []

    def new_block(self):
        pass
