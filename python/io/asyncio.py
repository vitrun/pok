#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright ©2014-04-16 Alex <zhirun.yu@duitang.com>
#
"""
async using eventlet
"""
import eventlet
from eventlet.green import socket

def busy_loop():
    while True:
        i = 0
        while i < 5000000:
            i += 1
        print "yielding"
        eventlet.sleep()
eventlet.spawn(busy_loop)

sock = socket.socket()
sock.connect(('192.168.172.2', 1234))
sock.send('foo\n' * 1024 * 1024 * 5)
print 'finished'
