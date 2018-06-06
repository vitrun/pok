import binascii
import json

from blockchain.key import ADDRESS_MAGIC_BYTE, Key


class Transaction(object):
    """A transaction"""
    def __init__(self, sender: str, recipient: str, payload: object,
                 public_key: str):
        self.sender = sender
        self.recipient = recipient
        self.payload = payload
        self.signature = None
        self.public_key = public_key

    def json(self):
        return {
            'sender': self.sender,
            'recipient': self.recipient,
            'payload': self.payload,
            'key': self.public_key
        }

    def sign(self, private_key):
        payload = json.dumps(self.json(), sort_keys=True, ensure_ascii=False)
        return Key(private_key).sign(payload)

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
                                     public_key=self.public_key)
