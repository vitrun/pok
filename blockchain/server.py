import tornado.ioloop
import requests
import tornado.web
import argparse
import json

import sys
sys.path.insert(0, '../')

from blockchain.node import Node
from blockchain.block import Block
from blockchain.transaction import Transaction

node = Node()


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Block):
            return obj.json()
        elif isinstance(obj, Transaction):
            return obj.json()
        return json.JSONEncoder.default(self, obj)


def ok(data=None):
    return json.dumps({'code': 0, 'data': data}, cls=ComplexEncoder)


def broadcat_block(doc, peers):
    for peer in peers:
        requests.post(peer+"/block/", data=doc)


def broadcast_trx(doc, peers):
    for peer in peers:
        requests.post(peer + "/transaction/", data=doc)


class BlockHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(ok(node.chain.blocks))

    def post(self):
        doc = json.loads(self.request.body)
        node.add_block(doc)
        #: broadcast the new block
        broadcat_block(doc)
        return ok()


class HeightHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(ok(node.chain.height))


class TransactionHandler(tornado.web.RequestHandler):
    def post(self):
        doc = json.loads(self.request.body)
        node.add_transaction(doc['sender_addr'], doc['sender_key'],
                             doc['recipient_addr'],
                             doc['payload'], doc['signature'])
        #: broadcast the new transaction
        broadcast_trx(doc)
        return ok()


class ConsensusHandler(tornado.web.RequestHandler):
    def get(self):
        #: find the longest chain
        max_height, target_peer = 0, None
        for peer in node.peers:
            res = requests.get(peer + "/chain/height/")
            height = int(res.json()['data'])
            if height > max_height:
                max_height, target_peer = height, peer
        #: fetch the blocks from target peer
        if max_height > node.chain.height:
            res = requests.get(target_peer + '/block/')
            block_docs = res.json()['data']
            node.chain.blocks = [Block.from_json(doc) for doc in block_docs]


def make_app():
    return tornado.web.Application([
        (r"/block/", BlockHandler),
        (r"/chain/height/", HeightHandler),
        (r"/transaction/", TransactionHandler),
        (r"/consensus/", ConsensusHandler),
    ])


if __name__ == "__main__":
    arger = argparse.ArgumentParser()
    arger.add_argument('port', type=str)
    arger.add_argument('--peers', type=str)
    args = arger.parse_args()
    if args.peers:
        node.peers = [p.strip() for p in args.peers.split(',')]
    node.init()

    app = make_app()
    app.listen(args.port)
    tornado.ioloop.IOLoop.current().start()
