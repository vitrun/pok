import tornado.ioloop
import tornado.web
import argparse
import json

import sys
sys.path.insert(0, '../')

from blockchain.node import Node

node = Node()


def ok(data=None):
    return json.dumps({'code': 0, 'data': data})


class BlockHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(ok(node.chain.blocks))

    def post(self):
        doc = json.loads(self.request.body)
        node.add_block()

class HeightHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(ok(node.chain.height))


class TransactionHandler(tornado.web.RequestHandler):
    def post(self):
        doc = json.loads(self.request.body)
        node.add_transaction(doc['sender_addr'], doc['sender_key'],
                             doc['recipient_addr'],
                             doc['payload'], doc['signature'])
        return ok()


def make_app():
    return tornado.web.Application([
        (r"/chain/block/", BlockHandler),
        (r"/chain/height/", HeightHandler),
        (r"/transaction/", TransactionHandler),
    ])


if __name__ == "__main__":
    arger = argparse.ArgumentParser()
    arger.add_argument('port', type=str)
    arger.add_argument('--peers', type=str)
    args = arger.parse_args()
    if args.peers:
        node.peers = [p.strip() for p in args.peers.split(',')]

    app = make_app()
    app.listen(args.port)
    tornado.ioloop.IOLoop.current().start()
