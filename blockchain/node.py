from blockchain.transaction import Transaction
from blockchain.block import Block

import time
import logging

logging.basicConfig(level=logging.INFO)


class Node(object):
    """
    A node
    """
    def __init__(self, peers=None):
        self.peers = peers or []

    @staticmethod
    def new_transaction(sender_addr, sender_key, recipient_addr, payload):
        """
        A new transaction to be included in next block
        """
        return Transaction(sender_addr, recipient_addr, payload, sender_key)

    @staticmethod
    def new_block(index, prev_hash, transactions):
        """
        Create new block with current transactions
        """
        if not transactions:
            return None
        start_t = time.time()
        while True:
            block = Block(index, prev_hash, transactions)
            if block.is_valid():
                logging.debug("Aha. Mined a valid block %s with nonce %s, "
                              "time: %d", block.hash, block.nonce,
                              time.time() - start_t)
                return block
            logging.debug("Mining, %d", block.nonce)
            block.increase_nonce()
