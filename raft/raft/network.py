import asyncio
import logging
import json


class UDPProtocol(asyncio.DatagramProtocol):
    def __init__(self, queue, request_handler_resolver, loop):
        self.queue = queue
        self.request_handler_resolver = request_handler_resolver
        self.loop = loop
        self.transport = None

    def __call__(self):
        return self

    async def start(self):
        while self.transport and not self.transport.is_closing():
            request = await self.queue.get()
            data = json.dumps(request['data'], ensure_ascii=False)
            # logging.debug('sending %s to %s', data, request['destination'])
            self.transport.sendto(data.encode('utf8'), request['destination'])

    def connection_made(self, transport):
        self.transport = transport
        asyncio.ensure_future(self.start(), loop=self.loop)

    def datagram_received(self, data, sender):
        # logging.debug('received %s from %s', data, sender)
        doc = json.loads(data)
        doc['sender'] = sender
        self.request_handler_resolver()(doc)

