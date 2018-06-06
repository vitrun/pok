import random
import hashlib
import ecdsa
import binascii


PUBKEY_MAGIC_BYTE = '\x04'
ADDRESS_MAGIC_BYTE = '\x06'


class Key(object):
    """
    Private/public key and address
    """
    _curve = ecdsa.curves.SECP256k1
    _hash_function = hashlib.sha1

    def __init__(self, private_key=None):
        if not private_key:
            seed = random.randrange(1, self._curve.order)
            self._private_key = ecdsa.keys.SigningKey.from_secret_exponent(
                seed, self._curve, self._hash_function
            )
        else:
            self._private_key = ecdsa.keys.SigningKey.from_string(
                private_key, self._curve, self._hash_function
            )

    @property
    def private_key(self):
        """
        :return: private key string
        """
        return self._private_key.to_string().hex()

    @property
    def public_key(self):
        """
        :return: public key string
        """
        ecdsa_public_key = self._private_key.get_verifying_key()
        return (PUBKEY_MAGIC_BYTE + ecdsa_public_key.to_string()).hex()

    @property
    def address(self):
        """
        :return: the address
        """
        ecdsa_public_key = self._private_key.get_verifying_key()
        return (ADDRESS_MAGIC_BYTE + ecdsa_public_key.to_string()).hex()

    def sign(self, data):
        """
        Sign something
        :return:
        """
        return self._private_key.sign(data.encode()).hex()

    def verify(self, data, signature):
        """
        Verify something
        :param data:
        :param signature:
        :return:
        """
        verify_key = self._private_key.get_verifying_key()
        return verify_key.verify(binascii.unhexlify(signature), data.encode())
