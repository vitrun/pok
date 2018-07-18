import logging


class Timer(object):
    """A timer"""
    def __init__(self, interval_millis, callback, loop):
        self.interval = interval_millis * 0.01
        self.callback = callback
        self.loop = loop
        self.handler = None
        self._is_active = False

    def start(self):
        self._is_active = True
        self.handler = self.loop.call_later(self.interval, self._run)

    def _run(self):
        if self._is_active:
            self.callback()
            # logging.warning('%s will be invoked %s seconds later', self.callback.__name__,
            #                 self.interval)
            self.handler = self.loop.call_later(self.interval, self._run)

    def reset(self):
        self.stop()
        self.start()

    def stop(self):
        self._is_active = False
        self.handler and self.handler.cancel()
        self.handler = None
