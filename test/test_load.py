# Copyright (C) 2010  Wil Mahan <wmahan+fatics@gmail.com>
#
# This file is part of FatICS.
#
# FatICS is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# FatICS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with FatICS.  If not, see <http://www.gnu.org/licenses/>.
#

"""
This a load test. You probably need to raise ulimit -n
to allow more open file descriptors.  Also, it probably won't
work with the default select() twisted reactor.  I assume
linux 2.6 and use epoll.

"""

import time
from twisted.trial import unittest
from twisted.conch import telnet
from twisted.internet import protocol, epollreactor
import cProfile
profile = 1

#from test import host, port
from test import *

#epollreactor.install()

from twisted.internet import reactor

conn_count = 8000
start_time = time.time()
conns = []
class TestProtocol(telnet.Telnet):
    def connectionMade(self):
        conns.append(self)
        self.i = len(conns)
        self.status = 'login'

    def dataReceived(self, data):
        if 'login:' in data:
            self.transport.write("guest\r\n\r\n")
        elif 'fics% ' in data:
            self.factory.num_done = self.factory.num_done + 1
            if self.i % 128 == 0:
                print '%f: %d done (%f users/sec)' % (time.time() - start_time, self.factory.num_done, self.factory.num_done / (time.time() - start_time))
            self.status = 'prompt'

    def quit(self):
        if (self.status != 'prompt'):
            print 'ERROR: state %s' % self.status
        #self.factory.tester.assert_(self.status == 'prompt')
        self.transport.write('quit\r\n')

        # self.transport.loseConnection()

    def connectionLost(self, reason):
        self.state = 'done'

class TestLoad(Test):
    def test_load(self):
        self._skip('slow test')
        fact = protocol.ClientFactory()
        fact.protocol = TestProtocol
        fact.tester = self
        fact.num_done = 0

        for i in xrange(0, conn_count):
            reactor.connectTCP(host, int(port), fact)

        reactor.callLater(500, self._shut_down)

        # Let's go
        if not profile:
            reactor.run()
        else:
            cProfile.runctx('reactor.run()', globals(), locals())

        for c in conns:
            self.assert_(c.state == 'done')
        print 'tested %d' % len(conns)

    def _shut_down(self):
        print "shutting down"
        for c in conns:
            c.quit()
        reactor.stop()

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
