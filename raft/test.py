import argparse
import asyncio

from raft.node import Node


async def start_cluster(node_cnt):
    pairs = [('127.0.0.1', 5600 + i) for i in range(node_cnt)]
    nodes = []
    for i in range(node_cnt):
        node = Node(('127.0.0.1', 5600 + i))
        nodes.append(node)

    for node in nodes:
        for pair in pairs:
            if node.port != pair[1]:
                node.add_node(pair)
        await node.start()


if __name__ == '__main__':
    arg = argparse.ArgumentParser()
    arg.add_argument('node_cnt', type=int, help='Number of nodes')
    args = arg.parse_args()
    loop = asyncio.get_event_loop()
    loop.create_task(start_cluster(args.node_cnt))
    loop.run_forever()

