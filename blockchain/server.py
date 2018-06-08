import tornado.ioloop
import tornado.web
import argparse
import json

import sys
sys.path.insert(0, '../')

from blockchain.node import Node

node = Node()


def sync_node(peers):
    pass


class BlockHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(json.dumps(node.chain.blocks))


def make_app():
    return tornado.web.Application([
      (r"/", BlockHandler),
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
