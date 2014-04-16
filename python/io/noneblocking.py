#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright ©2014-04-16 Alex <zhirun.yu@duitang.com>
#
"""
noneblocking
"""
import errno
import socket

sock = socket.socket()
sock.connect(('192.168.172.2', 1234))
sock.setblocking(0)

buf = buffer('foo\n' * 1024 * 1024 * 5)
while len(buf):
    try:
        buf = buf[sock.send(buf):]
    except socket.error, e:
        if e.errno != errno.EAGAIN:
            raise e
        print "I can do something"
print "finished"
