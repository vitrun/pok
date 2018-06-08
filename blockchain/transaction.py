import binascii
import json

from blockchain.key import ADDRESS_MAGIC_BYTE, Key


class Transaction(object):
    """A transaction"""
    def __init__(self, sender_addr: str, sender_key: str, recipient_addr: str,
                 payload: object):
        self.sender = sender_addr
        self.recipient = recipient_addr
        self.payload = payload
        self.signature = None
        self.sender_key = sender_key

    def json(self, with_sign=False):
        doc = {
            'sender': self.sender,
            'recipient': self.recipient,
            'payload': self.payload,
            'key': self.sender_key
        }
        if with_sign:
            doc['signature'] = self.signature
        return doc

    def sign(self, private_key):
        payload = json.dumps(self.json(), sort_keys=True, ensure_ascii=False)
        self.signature = Key(private_key).sign(payload)
        return self.signature

    def is_valid(self):
        """
        Check validity. addresses must be valid
        :return:
        """
        payload = json.dumps(self.json(), sort_keys=True, ensure_ascii=False)
        return binascii.unhexlify(self.sender).startswith(ADDRESS_MAGIC_BYTE) \
            and binascii.unhexlify(self.recipient)\
            .startswith(ADDRESS_MAGIC_BYTE) and \
            Key.verify_by_public_key(payload, signature=self.signature,
                                     public_key=self.sender_key)
