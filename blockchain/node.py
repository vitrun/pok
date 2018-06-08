from blockchain.transaction import Transaction
from blockchain.block import Block
from blockchain.chain import Chain

import time
import logging

logging.basicConfig(level=logging.INFO)


class Node(object):
    """
    A node
    """
    def __init__(self, peers=None):
        self.peers = peers or []
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
        self.chain.add_block(block)

    def add_transaction(self, sender_addr, sender_key, recipient_addr, payload,
                        signature):
        """
        A new transaction to be included in next block
        """
        transaction = Transaction(sender_addr, recipient_addr, payload,
                                  sender_key, signature)
        if transaction.is_valid():
            self.transactions.append(transaction)

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
