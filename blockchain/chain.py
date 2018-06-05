from blockchain.transaction import Transaction
from blockchain.block import Block

import time
import logging

logging.basicConfig(level=logging.INFO)


class Chain(object):
    """The chain"""
    def __init__(self):
        self.blocks = []
        self.current_transactions = []
        self._add_block(0, 1, [])

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

    def new_block(self):
        """
        Create new block with current transactions
        :return: <Block>
        """
        if not self.current_transactions:
            return None
        index, prev_hash = self.last_block.index + 1, self.last_block.hash
        return self._add_block(index, prev_hash, self.current_transactions)

    def _add_block(self, index, prev_hash, transactions):
        """
        Create a proof-of-work valid block
        :param index: <int>
        :param prev_hash: <str>
        :param transactions: <Transaction list>
        :return: <Block>
        """
        nonce, start_t = 0, time.time()
        while True:
            block = Block(index, nonce, prev_hash, transactions)
            if block.is_valid():
                self.blocks.append(block)
                logging.debug("Aha. Mined a valid block %s with nonce %s, "
                              "time: %d", block.hash, block.nonce,
                              time.time() - start_t)
                return block
            logging.debug("Mining, %d", nonce)
            nonce += 1

    @property
    def last_block(self):
        return self.blocks[-1] if self.blocks else None
