import requests
import logging
import tornado.ioloop
import tornado.web
import argparse
import random
import threading
import json
import time


class Node(object):
    def __init__(self):
        self.nodes = []
        self.port = None
        self.n = None
        self.v = None
        #: the cluster try to agree upon same state
        self.state = None
        #: to protect n
        self.lock = threading.Lock()
        self.reset()

    def reset(self):
        self.n = None
        self.v = None
        #: the cluster try to agree upon same state
        self.state = None

    def _init_n(self, n=None):
        """
        Init the n
        :return: True if newly initiated
        """
        with self.lock:
            if self.n:
                return False
            self.n = n or random.randrange(1, 10)
            return True

    def try_prepare(self, v):
        """
        Try to have other nodes' promises or learn about their suggestions
        """
        promises = []
        if not self._init_n():
            #: Already prepared or promised some other node
            return False

        for node in self.nodes:
            if node == self.port:
                continue
            res = requests.post('http://localhost:%s/prepare/' % node, json={
                'n': self.n
            })
            if res.ok():
                data = res.json()
                if int(data['n']) > self.n:
                    logging.warning('Refused by node ', node)
                    continue
                #: suggest should be [m, v]
                promises.append((data['n'], data['v']))
            else:
                logging.warning('Failed to contact ', node)
        return self._resolve(promises, v)

    def _resolve(self, promises, v):
        """
        Listen to other node's suggests if any, or use own value
        """
        answered = len(promises)
        if answered < (len(self.nodes) - 1) / 2:
            logging.warning('Failed to prepare, only %d/%d nodes answered', answered,
                            len(self.nodes))
            return False
        #: listen to suggest with max n or use v
        self.v, max_n = v, -1
        for suggest in promises:
            if suggest[0] > max_n and suggest[1]:
                max_n = suggest[0]
                self.v = suggest[1]
        logging.info('%d/%d nodes answered, will use v: %d by %s', answered, len(self.nodes),
                     self.v, 'other node' if max_n else 'me')
        return True

    def try_accept(self, v):
        """
        Try to make other nodes accept my value
        """
        accepts = []
        for node in self.nodes:
            if node == self.port:
                continue
            res = requests.post('http://localhost:%d/accept/', json={
                'n': self.n,
                'v': v,
            })
            if res.ok():
                data = res.json()
                if int(data['n']) != self.n:
                    logging.warning('Node %d betrayed with n: %d. mine: %d', node, data['n'],
                                    self.n)
                    continue
                if data['v'] == self.v:
                    accepts.append(node)
                else:
                    logging.error('Node %d accept my n: %d, but returned v: %d', node, self.n,
                                  data['v'])
        if len(accepts) < (len(self.nodes) - 1) / 2:
            logging.warning('Failed to accept, only %d/%d accepted', len(accepts), len(self.nodes))
            return False
        else:
            logging.info('Accepted. with %d/%d nodes', len(accepts), len(self.nodes))
            self.state = v
            return True

    def promised(self, n):
        """
        Promise some node that I won't accept others
        """
        if self._init_n(n):
            #: Got my promise
            return n, None
        return n, self.v

    def accepted(self, n, v):
        """
        Accept the n, v pair
        """
        if self.n == n and self.v == v:
            logging.warning('Accepted, set my state to %d', v)
            self.state = v
            return n, v
        else:
            logging.warning('Can not accept n:%d, v:%d. My n: %d, my v: %d', n, v, self.n, self.v)
            return self.n, self.v


paxos_node = Node()


def ok(data=None):
    return json.dumps({'code': 0, 'data': data or {}})


class StateHandler(tornado.web.RequestHandler):
    def post(self):
        val = int(self.get_argument('value'))
        res = paxos_node.try_prepare(val)
        self.write(ok(res))


class ResetHandler(tornado.web.RequestHandler):
    def post(self):
        paxos_node.reset()
        self.write(ok(True))


class PrepareHandler(tornado.web.RequestHandler):
    def post(self):
        doc = json.loads(self.request.body)
        n, v = paxos_node.promised(doc['n'])
        self.write(ok({
            'n': n,
            'v': v
        }))


class AcceptHandler(tornado.web.RequestHandler):
    def post(self):
        doc = json.loads(self.request.body)
        my_n, my_v = paxos_node.accepted(doc['n'], doc['v'])
        self.write(ok({
            'n': my_n,
            'v': my_v
        }))


def make_app():
    return tornado.web.Application([
        (r"/state/", StateHandler),
        (r"/accept/", AcceptHandler),
        (r"/prepare/", PrepareHandler),
        (r"/reset/", ResetHandler),
    ])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('port', type=int, help='HTTP port')
    parser.add_argument('--fail', type=float, help='network failure ratio')
    parser.add_argument('--nodes', type=str, help='node list')
    args = parser.parse_args()

    if args.nodes:
        paxos_node.nodes = args.nodes.split(',')
    if args.port:
        app = make_app()
        app.listen(args.port)
        tornado.ioloop.IOLoop.current().start()
