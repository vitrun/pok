from blockchain.block import Block
from blockchain.chain import Chain

import time
import logging

logging.basicConfig(level=logging.INFO)


class Node(object):
    """
    A node
    """

    TRX_PER_BLOCK = 2

    def __init__(self):
        self.transactions = []
        self.chain = Chain()

    def init(self, blocks=None):
        """
        Sync blocks from other nodes or mine the genesis block
        """
        if blocks:
            for b in blocks:
                self.chain.add_block(b)
        else:
            block = self.mine_block(0, 0, [])
            self.chain.add_block(block)

    def add_block(self, doc):
        block = Block.from_json(doc)
        if block.index == self.chain.height:
            self.chain.add_block(block)

    def add_transaction(self, transaction):
        """
        A new transaction to be included in next block
        """
        if transaction.is_valid():
            self.transactions.append(transaction)

    def mine(self):
        if len(self.transactions) > self.TRX_PER_BLOCK:
            logging.info("mining new block")
            block = Node.mine_block(self.chain.height,
                                    self.chain.last_block.hash,
                                    self.transactions)
            self.chain.add_block(block)
            #: clear
            self.transactions = []
            return block
        return None

    @staticmethod
    def mine_block(index, prev_hash, transactions):
        """
        Create new block with current transactions
        """
        start_t = time.time()
        block = Block(index, prev_hash, transactions)
        while True:
            if block.is_valid():
                logging.debug("Aha. Mined a valid block %s with nonce %s, "
                              "time: %d", block.hash, block.nonce,
                              time.time() - start_t)
                return block
            logging.debug("Mining, %d", block.nonce)
            block.increase_nonce()
