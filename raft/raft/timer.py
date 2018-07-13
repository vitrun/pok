
class Timer(object):
    """A timer"""
    def __init__(self, interval_millis, callback, loop):
        self.interval = interval_millis * 0.01
        self.callback = callback
        self.loop = loop
        self.handler = None

    def start(self):
        # self.callback()
        self.handler = self.loop.call_later(self.interval, self.callback)

    def reset(self):
        self.stop()
        self.start()

    def stop(self):
        self.handler and self.handler.cancel()
        self.handler = None
