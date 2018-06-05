import sys
sys.path.insert(0, '../')

from blockchain.chain import Chain


def test_chain_init():
    """
    test chain init
    """
    #import ipdb; ipdb.set_trace()
    chain = Chain()
    assert chain.blocks[0].hash.startswith('000')
