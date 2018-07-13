"""
A simple demo for raft consensus with in-memory log. To play:
1. Start a cluster by registering new nodes
2. Send command to any node
3. Show each node's log to check the log replication process
4. Kill the Leader to check the leader election process
"""
import asyncio
import logging
from .network import UDPProtocol
from .state import Follower, Candidate, Leader


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s.%(msecs)03d %(levelname)s '
                           '%(module)s: %(message)s')


class Node:
    """Raft Node (Server)"""

    def __init__(self, address):
        self.host, self.port = address
        self.peers = []
        self.id = '{}:{}'.format(self.host, self.port)

        self.loop = asyncio.get_event_loop()
        self.state = Follower(self)
        self.requests = asyncio.Queue(loop=self.loop)
        self.transport = None

    def request_handler_resolver(self):
        return self.state.request_handler

    async def start(self):
        protocol = UDPProtocol(
            queue=self.requests,
            request_handler_resolver=self.request_handler_resolver,
            loop=self.loop
        )

        address = self.host, self.port
        self.transport, _ = await asyncio.Task(
            self.loop.create_datagram_endpoint(protocol, local_addr=address),
            loop=self.loop
        )
        logging.info('node %s started, peers: %s', self.id, self.peers)
        self.state.start()

    def stop(self):
        self.state.stop()
        self.transport.close()

    def add_node(self, host_port_tuple):
        self.peers.append(host_port_tuple)

    @property
    def cluster_count(self):
        return len(self.peers) + 1

    async def send(self, data, destination):
        """Sends data to destination Node
        Args:
            data — serializable object
            destination — <str> '127.0.0.1:8000' or <tuple> (127.0.0.1, 8000)
        """
        if isinstance(destination, str):
            host, port = destination.split(':')
            destination = host, int(port)
        await self.requests.put({
            'data': data,
            'destination': destination
        })

    def broadcast(self, data):
        """Sends data to all Nodes in cluster"""
        for destination in self.peers:
            # logging.debug('sending %s to %s', data, destination)
            asyncio.ensure_future(self.send(data, destination), loop=self.loop)

    def is_majority(self, count):
        return count > (self.cluster_count // 2)

    def to_candidate(self):
        self._change_state(Candidate)

    def to_leader(self):
        self._change_state(Leader)

    def to_follower(self):
        self._change_state(Follower)

    def _change_state(self, new_state):
        self.state.stop()
        logging.debug('state of node %s changed from %s to %s', self.id,
                      self.state.__class__.__name__, new_state.__name__)
        self.state = new_state(self)
        self.state.start()
