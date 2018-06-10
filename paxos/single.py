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
        #: number we'll prepare with
        self.n = None
        #: value to propose
        self.v = None
        #: try to agree upon this state
        self.state = None
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
        if self.n:
            return False
        self.n = n or random.randrange(1, 10)
        return True

    def try_prepare(self, v, sleep=0):
        """
        Try to have other nodes' promises or learn about their suggestions
        """
        promises = []
        if not self._init_n():
            #: Already prepared or promised some other node
            logging.warning('I have promised with %d', self.n)
            return False

        random.shuffle(self.nodes)
        for node in self.nodes:
            if int(node) == self.port:
                continue
            logging.warning('Sleep for %s seconds. Please try to set the state to some different '
                            'value by requesting another node. Check how the cluster will react.',
                            sleep)

            try:
                res = requests.post('http://localhost:%s/prepare/' % node, json={
                    'n': self.n
                }, timeout=3)
                if res.ok:
                    data = res.json()['data']
                    if int(data['n']) > self.n:
                        logging.warning('Refused by node %d', node)
                        continue
                    #: suggest should be [m, v]
                    promises.append((data['n'], data['v']))
                else:
                    logging.warning('Failed to contact %d', node)
            except Exception as e:
                logging.error('Failed when try_prepare: %s', e)
            time.sleep(sleep)

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
        self.v, max_n, use_other = v, 0, False
        for suggest in promises:
            if suggest[0] > max_n and suggest[1]:
                max_n = suggest[0]
                self.v = suggest[1]
                use_other = True
        logging.info('%d/%d nodes answered, will use v: %d by %s', answered, len(self.nodes),
                     self.v, 'other node' if use_other else 'me')
        return True

    def try_accept(self, v):
        """
        Try to make other nodes accept my value
        """
        accepts = []
        random.shuffle(self.nodes)
        print(self.nodes)
        for node in self.nodes:
            if int(node) == self.port:
                continue
            try:
                res = requests.post('http://localhost:%s/accept/' % node, json={
                    'n': self.n,
                    'v': v,
                }, timeout=3)
                if res.ok:
                    data = res.json()['data']
                    if data['v'] == self.v:
                        accepts.append(node)
                        if int(data['n']) > self.n:
                            logging.warning('Node %s overwhelmed with n: %s. mine: %s', node,
                                            data['n'],
                                            self.n)
                    else:
                        logging.error('Node %s accept my n: %s, but returned v: %s', node, self.n,
                                      data['v'])
            except Exception as e:
                logging.warning('Failed to contact node %d: %s', node, e)

        if len(accepts) < (len(self.nodes) - 1) / 2:
            logging.warning('Failed to accept, only %d/%d accepted', len(accepts), len(self.nodes))
            return False
        else:
            logging.info('Accepted. with %d/%d nodes', len(accepts), len(self.nodes))
            self.state = v
            return True

    def try_teach(self):
        """
        Broadcast the state to all learners
        """
        if not self.state:
            return
        random.shuffle(self.nodes)
        for node in self.nodes:
            if node == self.port:
                continue
            try:
                res = requests.post('http://localhost:%d/learn/' % node, json={
                    'state': self.state
                }, timeout=3)
                if res.ok:
                    logging.info("Node %d has learned sate %d", node, self.state)
            except Exception as e:
                logging.warning('Failed to teach node %d', node)

    def promised(self, n):
        """
        Promise some node that I won't accept others
        """
        if self._init_n(n):
            #: Got my promise
            return n, None
        return self.n, self.v

    def accepted(self, n, v):
        """
        Accept the n, v pair
        """
        if self.n == n:
            logging.warning('Accepted, set my v to %d', v)
            self.v = v
            return n, v
        else:
            logging.warning('Can not accept n:%s, v:%s. My n: %s, my v: %s', n, v, self.n, self.v)
            return self.n, self.v

    def learned(self, state):
        """
        Learn the conclusion
        """
        self.state = state


paxos_node = Node()


def delay():
    delta = random.randrange(1, 10)
    time.sleep(0.3 + delta * 0.2)


def ok(data=None):
    return json.dumps({'code': 0, 'data': data or {}})


class StateHandler(tornado.web.RequestHandler):
    def post(self):
        if paxos_node.state:
            self.write(ok('State is resolved. please reset.'))
            return
        val = int(self.get_argument('value'))
        delay = int(self.get_argument('delay', 0))
        res = paxos_node.try_prepare(val, delay)
        accepted = False
        if res:
            accepted = paxos_node.try_accept(paxos_node.v)
        self.finish(ok({'state': paxos_node.state}))
        if accepted:
            paxos_node.try_teach()

    def get(self):
        self.finish(ok({
            'state': paxos_node.state,
            'n': paxos_node.n,
            'v': paxos_node.v
        }))


class ResetHandler(tornado.web.RequestHandler):
    def post(self):
        paxos_node.reset()
        self.finish(ok(True))


class PrepareHandler(tornado.web.RequestHandler):
    def post(self):
        doc = json.loads(self.request.body)
        n, v = paxos_node.promised(doc['n'])
        delay()
        self.finish(ok({
            'n': n,
            'v': v
        }))


class AcceptHandler(tornado.web.RequestHandler):
    def post(self):
        doc = json.loads(self.request.body)
        my_n, my_v = paxos_node.accepted(doc['n'], doc['v'])
        delay()
        self.finish(ok({
            'n': my_n,
            'v': my_v
        }))


class LearnHandler(tornado.web.RequestHandler):
    def post(self):
        doc = json.loads(self.request.body)
        paxos_node.learned(doc['state'])
        self.finish(ok())


def make_app():
    return tornado.web.Application([
        (r"/state/", StateHandler),
        (r"/accept/", AcceptHandler),
        (r"/prepare/", PrepareHandler),
        (r"/reset/", ResetHandler),
        (r"/learn/", LearnHandler),
    ])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('port', type=int, help='HTTP port')
    parser.add_argument('--nodes', type=str, help='node list')
    args = parser.parse_args()

    if args.nodes:
        paxos_node.nodes = [int(n) for n in args.nodes.split(',')]
    if args.port:
        paxos_node.port = args.port
        app = make_app()
        app.listen(args.port)
        tornado.ioloop.IOLoop.current().start()
