import sys
sys.path.insert(0, '../')

from blockchain.chain import Chain
from blockchain.key import Key


def test_chain_init():
    """
    test chain init
    """
    chain = Chain()
    assert chain.blocks[0].hash.startswith('000')


def test_key_sign():
    """
    test key generation
    """
    key = Key()
    assert key.private_key

    payload = 'Hello world'
    signature = key.sign(payload)
    assert signature


def test_key_verify():
    payload = 'Hello world'
    key = Key()
    signature = key.sign(payload)
    print(signature)
    assert key.verify(payload, signature)
