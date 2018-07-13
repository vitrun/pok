
class Timer(object):
    """A timer"""
    def __init__(self, interval_millis, callback, loop):
        self.interval = interval_millis * 0.001
        self.callback = callback
        self.loop = loop
        self.handler = None

    def start(self):
        self.callback()
        self.handler = self.loop.call_latter(self.interval, self.callback)

    def reset(self):
        self.stop()
        self.start()

    def stop(self):
        self.handler.cancel()
        self.handler = None
