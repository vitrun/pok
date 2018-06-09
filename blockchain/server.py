import tornado.ioloop
import requests
import tornado.web
import random
import logging
import argparse
import json

import sys
sys.path.insert(0, '../')

from blockchain.node import Node
from blockchain.block import Block
from blockchain.key import Key
from blockchain.transaction import Transaction

node = Node()
node.init()
peers = []


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Block):
            return obj.json()
        elif isinstance(obj, Transaction):
            return obj.json()
        return json.JSONEncoder.default(self, obj)


def ok(data=None):
    return json.dumps({'code': 0, 'data': data or {}}, cls=ComplexEncoder)


def broadcast_block(doc):
    ttl = doc.get('ttl', 1)
    if ttl == 0:
        return
    doc['ttl'] = ttl - 1
    for peer in peers:
        if random.randrange(1, 20) > 10:
            #: network failure
            continue
        logging.info("broadcasting block: %s to peer %s", doc['index'], peer)
        requests.post(peer+"/block/", json=doc)


def broadcast_trx(doc):
    ttl = doc.get('ttl', 1)
    if ttl == 0:
        return
    doc['ttl'] = 0
    for peer in peers:
        #: network failure
        if random.randrange(1, 20) > 13:
            continue
        logging.info("broadcasting transaction: %s to peer %s", doc['payload'],
                     peer)
        requests.post(peer + "/transaction/", json=doc)


class BlockHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(ok(node.chain.blocks))

    def post(self):
        doc = json.loads(self.request.body)
        node.add_block(doc)
        #: broadcast the new block
        self.finish(ok())
        broadcast_block(doc)


class HeightHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(ok(node.chain.height))


class TransactionHandler(tornado.web.RequestHandler):
    def post(self):
        doc = json.loads(self.request.body)
        trx = Transaction(doc['sender_addr'], doc['sender_public'],
                          doc['recipient_addr'], doc['payload'])
        trx.sign(doc['sender_private'])
        #: broadcast the new transaction
        broadcast_trx(doc)
        new_block = node.add_transaction(trx)
        #: broadcast new blocks
        self.finish(ok())
        if new_block:
            logging.info("mined new block: %s", new_block.index)
            broadcast_block(new_block.json())


class ConsensusHandler(tornado.web.RequestHandler):
    def post(self):
        #: find the longest chain
        max_height, target_peer = 0, None
        for peer in peers:
            res = requests.get(peer + "/chain/height/")
            height = int(res.json()['data'])
            if height > max_height:
                max_height, target_peer = height, peer
        #: fetch the blocks from target peer
        if max_height > node.chain.height:
            logging.info('found longer chain %d. replace mine %d', max_height,
                         node.chain.height)
            res = requests.get(target_peer + '/block/')
            block_docs = res.json()['data']
            node.chain.blocks = [Block.from_json(doc) for doc in block_docs]
        self.write(ok())


class MineHandler(tornado.web.RequestHandler):
    def post(self):
        node.mine()
        self.write(ok())


def make_app():
    return tornado.web.Application([
        (r"/block/", BlockHandler),
        (r"/chain/height/", HeightHandler),
        (r"/transaction/", TransactionHandler),
        (r"/consensus/", ConsensusHandler),
        (r"/mine/", MineHandler),
    ])


if __name__ == "__main__":
    arger = argparse.ArgumentParser()
    subparsers = arger.add_subparsers(help='commands')
    node_parser = subparsers.add_parser('node', help='node')
    node_parser.set_defaults(which='node')
    node_parser.add_argument('port', type=str)
    node_parser.add_argument('--peers', type=str)

    key_parser = subparsers.add_parser('key', help='keygen')
    key_parser.set_defaults(which='key')
    sign_parser = subparsers.add_parser('sign', help='sign')
    sign_parser.set_defaults(which='sign')
    sign_parser.add_argument('private', type=str, help='private key')

    args = arger.parse_args()
    if args.which == 'node' and args.port:
        if args.peers:
            peers = [p.strip() for p in args.peers.split(',')]
        app = make_app()
        app.listen(args.port)
        tornado.ioloop.IOLoop.current().start()
    else:
        key = Key()
        print('private: %s\npublic: %s\naddress: %s\n' % (key.private_key,
              key.public_key, key.address))
