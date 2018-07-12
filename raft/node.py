"""
A simple demo for raft consensus with in-memory log. To play:
1. Start a cluster by registering new nodes
2. Send command to any node
3. Show each node's log to check the log replication process
4. Kill the Leader to check the leader election process
"""
import asyncio
from .network import UDPProtocol
from .state import Follower


class Node:
    """Raft Node (Server)"""

    nodes = []

    def __init__(self, address):
        self.host, self.port = address
        self.cluster = set()

        self.loop = asyncio.get_event_loop()
        self.state = Follower(self)
        self.requests = asyncio.Queue(loop=self.loop)
        self.__class__.nodes.append(self)
        self.transport = None

    async def start(self):
        protocol = UDPProtocol(
            queue=self.requests,
            request_handler=self.state.request_handler,
            loop=self.loop
        )

        address = self.host, self.port
        self.transport, _ = await asyncio.Task(
            self.loop.create_datagram_endpoint(protocol, local_addr=address),
            loop=self.loop
        )
        self.state.start()

    def stop(self):
        self.state.stop()
        self.transport.close()

    def update_cluster(self, address_list):
        self.cluster.update({address_list})

    @property
    def cluster_count(self):
        return len(self.cluster)

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
        for destination in self.cluster:
            asyncio.ensure_future(self.send(data, destination), loop=self.loop)

    def is_majority(self, count):
        return count > (self.cluster_count // 2)

