from hashlib import sha256


class Node(object):
    """
    Each node as, as attributes, references to left and right children, parent and sibling node.
    """

    def __init__(self, data):
        self.val = sha256(str(data).encode('utf8')).hexdigest()
        self.l = None
        self.r = None
        self.p = None
        self.sib = None


class MerkleTree(object):
    """
    Added values are stored in a list until the tree is built.
    """

    def __init__(self, data_list=None):
        self.leaves = data_list and [Node(data) for data in data_list] or []
        self.root = None

    def add(self, data):
        self.leaves.append(Node(data))

    def build(self):
        """
        Build up the whole tree from the leaves
        """
        # copy the leaves
        layer = self.leaves[::]
        # reduce the leaves to exactly one node
        while len(layer) != 1:
            layer = self._build(layer)
        self.root = layer[0]

    @staticmethod
    def _build(layer):
        """
        Build the next aggregation level
        """
        # duplicate the last element if it has odd elements
        if len(layer) % 2:
            layer.append(layer[-1])
        new_layer = []
        for idx in range(0, len(layer), 2):
            node = Node(layer[idx].val + layer[idx + 1].val)
            node.l, node.r = layer[idx], layer[idx + 1]
            layer[idx].p, layer[idx + 1].p = node, node
            layer[idx].sib, layer[idx + 1].sib = layer[idx + 1].sib, layer[idx].sib
            new_layer.append(node)
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


if __name__ == '__main__':
    # build
    tree = MerkleTree(range(20))
    tree.build()
    print(tree.root.val)

    # validate
    print('valid: ', tree.validate())
