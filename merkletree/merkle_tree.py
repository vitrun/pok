#encoding:utf8

from hashlib import sha256


class Node(object):
    """
    Each node as, as attributes, references to left and right children, parent
    """

    def __init__(self, data=None):
        self.val = data is not None and sha256(data).hexdigest() or None
        self.l = None
        self.data = data
        # height
        self.h = 0
        self.r = None
        self.p = None


class MerkleTree(object):
    """
    Added values are stored in a list until the tree is built.
    """

    def __init__(self, data_list=None):
        self.leaves = data_list and [Node(data) for data in data_list] or []
        self.root = None
        self.build()

    def build(self):
        """
        Build up the whole tree from the leaves
        """
        # copy the leaves
        height, layer = 0, self.leaves[::]
        # reduce the leaves to exactly one node
        while len(layer) != 1:
            layer = self._build(layer, height)
            height += 1
        self.root = layer[0]

    @staticmethod
    def _build(layer, height):
        """
        Build the next aggregation level
        """
        if len(layer) == 1:
            return layer
        odd = None
        if len(layer) % 2:
            # promote to higher level
            odd = layer.pop(-1)
            # layer.append(layer[-1])
        new_layer = []
        for idx in range(0, len(layer), 2):
            node = Node(layer[idx].val + layer[idx + 1].val)
            node.h = height + 1
            node.l, node.r = layer[idx], layer[idx + 1]
            layer[idx].p, layer[idx + 1].p = node, node
            new_layer.append(node)
        if odd:
            odd.h += 1
            new_layer.append(odd)
        return new_layer

    def validate(self):
        """
        verify the tree by traversing the nodes and reproduce the hash
        """
        return self._validate(self.root)

    @staticmethod
    def _validate(node):
        if not (node.l and node.r):
            return True
        return node.val == Node(node.l.val + node.r.val).val and MerkleTree._validate(node.l) and \
            MerkleTree._validate(node.r)

    def append(self, data):
        """
        append new data.
        """
        # FIXME. do not recalculate the whole thing
        self.leaves.append(Node(data))
        self.build()

    def echo(self):
        """
        print the tree
        """
        last_node, l, buffer = None, [self.root], ''
        while l:
            node = l.pop(0)
            if last_node and last_node.h != node.h:
                print(buffer)
                buffer = ''
            buffer += '%6s' % node.data[-4:]
            if node.l:
                l.append(node.l)
            if node.r:
                l.append(node.r)
            last_node = node
        print(buffer)

    def contains(self, data, pos):
        """
        Check if data is in specific position
        """
        node = self.leaves[pos]
        tmp = Node(data)
        while node != self.root:
            if tmp.val != node.val:
                return False
            if not node.p:
                break
            if node.p.l == node:
                # I'm the left node
                tmp = Node(tmp.val + node.p.r.val)
            else:
                # I'm the right node
                tmp = Node(node.p.l.val + tmp.val)
            # import ipdb; ipdb.set_trace()
            node = node.p
        return tmp.val == self.root.val


if __name__ == '__main__':
    # build
    tree = MerkleTree(['a', '3', '你'])
    print(tree.root.val)
    # validate
    print('valid: ', tree.validate())
    tree.echo()
    # contains
    print(tree.contains('你', 2))
