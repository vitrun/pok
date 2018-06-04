from transaction import Transaction
from block import Block


class Chain(object):
    """The chain"""
    def __init__(self):
        self.blocks = []
        self.current_transactions = []
        self.new_block(1, 1)

    def new_transaction(self, sender, recipient, amount):
        """
        A new transaction to be included in next block
        :param sender: <str> address of sender
        :param recipient: <str> address of recipient
        :param amount: <float> amount
        :return: <int> the containing block index
        """
        trx = Transaction(sender, recipient, amount)
        self.current_transactions.append(trx)

    def new_block(self, proof, previous_hash):
        prev_index = self.last_block.index + 1 if self.last_block else 1
        block = Block(prev_index, proof, previous_hash, self.current_transactions)
        self.blocks.append(block)
        return block

    @property
    def last_block(self):
        return self.blocks[-1] if self.blocks else None
