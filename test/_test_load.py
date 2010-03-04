from test import *

import time

"""
This a load test. You probably need to raise ulimit -n
to allow more open file descriptors.  Also, it probably won't
work with the default select() twisted reactor; I suggest epoll,
assuming Linux 2.6.

"""

class TestLoad(Test):
    def test_load(self):
        conns = []
        for i in range(1, 3000):
             conns.append(self.connect_as_guest())

        print "ok done"

        time.sleep(200)

        for conn in conns:
            self.close(conn)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
