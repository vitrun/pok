import json
import _sha256

from blockchain.transaction import Transaction


class Block(object):
    """The block structure"""
    difficulty = 1

    def __init__(self, index, prev_hash, transactions, nonce=0):
        self.index = index
        self.nonce = nonce
        self.prev_hash = prev_hash
        self.transactions = transactions

    def increase_nonce(self):
        self.nonce += 1

    @staticmethod
    def from_json(doc):
        trxs = [Transaction(**tdoc) for tdoc in doc['transactions']]
        return Block(doc['index'], doc['prev_hash'], trxs, doc['nonce'])

    def json(self):
        return {
            'index': self.index,
            'nonce': self.nonce,
            'prev_hash': self.prev_hash,
            'transactions': [trx.json(with_sign=True) for trx in
                             self.transactions]
        }

    @property
    def hash(self):
        """
        Make a hash
        :return: <str>
        """
        doc = self.json()
        block_str = json.dumps(doc, sort_keys=True, ensure_ascii=False)
        return _sha256.sha256(block_str.encode()).hexdigest()

    def is_valid(self):
        """
        Whether it is a valid block
        :return: <Bool>
        """
        return all([trx.is_valid() for trx in self.transactions])\
            and Block.proof_of_work(self, Block.difficulty)

    @staticmethod
    def proof_of_work(block, difficulty):
        """
        Whether the length of proceeding 0s is difficulty
        :param block: <Block>
        :param difficulty: <Integer> length of proceeding zeros
        :return: <Bool>
        """
        return block.hash.startswith('0' * difficulty)

