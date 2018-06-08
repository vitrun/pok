
class Chain(object):
    """The chain"""
    def __init__(self):
        self.blocks = []

    @property
    def last_block(self):
        return self.blocks[-1] if self.blocks else None

    @property
    def height(self):
        return len(self.blocks)

    def is_valid(self):
        """
        Validate the chain
        """
        for idx, block in enumerate(self.blocks):
            if not block.is_valid():
                return False
            if idx != 0 and self.blocks[idx-1].hash != block.prev_hash:
                return False
        return True

    def add_block(self, block):
        if block.is_valid():
            if not self.last_block:
                self.blocks.append(block)
            elif self.last_block.hash == block.prev_hash:
                self.blocks.append(block)

