#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright ©2014-03-29 Alex <zhirun.yu@duitang.com>
#
"""
blocking
"""

import socket

sock = socket.socket()
sock.connect(('192.168.172.2', 1234))
sock.send('foo\n' * 1024 * 1024 * 5)
print 'finished'
