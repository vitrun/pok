import sys
sys.path.insert(0, '../')

from blockchain.chain import Chain
from blockchain.key import Key
from blockchain.block import Block
from blockchain.node import Node
from blockchain.transaction import Transaction


def test_chain_init():
    """
    test chain init
    """
    chain = Chain()
    assert not chain.last_block


def test_key_init():
    key = Key()
    key2 = Key(key.private_key)
    assert key.private_key == key2.private_key


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


def test_public_verify():
    key = Key()
    payload = 'Hello world'
    signature = key.sign(payload)
    Key.verify_by_public_key(payload, signature, key.public_key)


def test_transaction_validation():
    sender, recipient = Key(), Key()
    trx = Transaction(sender.address, sender.public_key, recipient.address,
                      'Hello world')
    trx.signature = trx.sign(sender.private_key)
    assert trx.is_valid()


def test_block_validation():
    sender, recipient = Key(), Key()
    trx = Transaction(sender.address, sender.public_key, recipient.address,
                      'Hello world')
    trx.sign(sender.private_key)
    assert Node.mine_block(0, 0, [trx]).is_valid()


def test_chain_validation():
    chain = Chain()

    sender, recipient = Key(), Key()
    trx = Transaction(sender.address, sender.public_key,
                      recipient.address, "Hi")
    trx.sign(sender.private_key)
    genesis = Node.mine_block(0, 0, [trx])
    chain.add_block(genesis)
    for _ in range(1, 3):
        trx = Transaction(sender.address, sender.public_key,
                          recipient.address, "Hi")
        trx.sign(sender.private_key)
        block = Node.mine_block(chain.height, chain.last_block.hash, [trx])
        chain.add_block(block)

    assert chain.is_valid()
