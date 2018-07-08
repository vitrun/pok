import requests
import logging
import tornado.ioloop
import tornado.web
import argparse
import random
import json
import time

logging.basicConfig(level=logging.INFO)


class Node(object):
    def __init__(self):
        self.nodes = []
        self.port = None
        self.reset()

    def reset(self):
        pass



raft_node = Node()


def ok(data=None):
    return json.dumps({'code': 0, 'data': data or {}})


# class PrepareHandler(tornado.web.RequestHandler):
#     def post(self):
#         doc = json.loads(self.request.body)
#         n, v = paxos_node.promised(doc['n'])
#         delay()
#         self.finish(ok({
#             'n': n,
#             'v': v
#         }))
#
#
# class AcceptHandler(tornado.web.RequestHandler):
#     def post(self):
#         doc = json.loads(self.request.body)
#         my_n, my_v = paxos_node.accepted(doc['n'], doc['v'])
#         delay()
#         self.finish(ok({
#             'n': my_n,
#             'v': my_v
#         }))
#
#
# class LearnHandler(tornado.web.RequestHandler):
#     def post(self):
#         doc = json.loads(self.request.body)
#         paxos_node.learned(doc['state'])
#         self.finish(ok())
#

def make_app():
    return tornado.web.Application([
        # (r"/learn/", LearnHandler),
    ])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('port', type=int, help='HTTP port')
    parser.add_argument('--nodes', type=str, help='node list')
    args = parser.parse_args()


