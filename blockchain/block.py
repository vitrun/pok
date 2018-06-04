import time


class Block(object):
    """The block structure"""
    def __init__(self, index, proof, prev_hash, transactions):
        self.index = index
        self.timestamp = time.time()
        self.proof = proof
        self.prev_hash = prev_hash
        self.transactions = transactions

