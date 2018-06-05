import time
import json
import _sha256


class Block(object):
    """The block structure"""
    difficulty = 4

    def __init__(self, index, prev_hash, transactions):
        self.index = index
        self.timestamp = time.time()
        self.nonce = 0
        self.prev_hash = prev_hash
        self.transactions = transactions

    def increase_nonce(self):
        self.nonce += 1

    @property
    def hash(self):
        """
        Make a hash
        :return: <str>
        """
        doc = {
            'index': self.index,
            'timestamp': self.timestamp,
            'nonce': self.nonce,
            'prev_hash': self.prev_hash,
            'transactions': self.transactions
        }
        block_str = json.dumps(doc, sort_keys=True, ensure_ascii=True)
        return _sha256.sha256(block_str.encode()).hexdigest()

    def is_valid(self):
        """
        Whether it is a valid block
        :return: <Bool>
        """
        return Block.proof_of_work(self, Block.difficulty)

    @staticmethod
    def proof_of_work(block, difficulty):
        """
        Whether the length of proceeding 0s is difficulty
        :param block: <Block>
        :param difficulty: <Integer> length of proceeding zeros
        :return: <Bool>
        """
        return block.hash.startswith('0' * difficulty)

