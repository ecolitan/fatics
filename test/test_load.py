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
linux 2.6 and epoll.

"""

import sys
import time

from twisted.internet import epollreactor
epollreactor.install()

from twisted.trial import unittest
from twisted.internet import protocol, defer
#import cProfile
#profile = 0

from .test import *

from twisted.internet import reactor

#conn_count = 8000
# For some reason the load test still hangs for a larger number of users.
# It seems to be a problem with the twisted test, not the server.
conn_count = 1000
start_time = time.time()
class TestProtocol(protocol.Protocol):
    state = 'unconnected'
    allData = ''
    def connectionMade(self):
        self.state = 'connectionMade'
        self.factory.conns.append(self)
        #self.i = len(self.factory.conns)
        #self.transport.setTcpNoDelay(True)

    def dataReceived(self, data):
        self.allData += data
        if 'login:' in data:
            self.state = 'login'
            self.transport.write("guest\r\n\r\n")
        elif 'fics% ' in data:
            self.state = 'prompt'
            self.factory.num_done += 1
            if self.factory.num_done % 128 == 0:
                print('%f: %d done (%f users/sec)' % (time.time() - start_time, self.factory.num_done, self.factory.num_done / (time.time() - start_time)))
            if self.factory.num_done == conn_count:
                print('finished with all %d logins' % conn_count)
                self.factory.tester.shut_down()
                self.factory.tester.finished.callback(self)
        elif 'limit for guests' in data:
            print('ERROR: limit for guests reached')
            self.transport.loseConnection()
            self.factory.error = 1

    def quit(self):
        if (self.state != 'prompt'):
            print('ERROR: state %s' % self.state)
            self.factory.error = 1
        #self.factory.tester.assert_(self.status == 'prompt')
        self.transport.write('quit\r\n')

        self.transport.loseConnection()
        self.factory.conns.remove(self)

    def connectionLost(self, reason):
        self.state = 'connectionLost'

class TestLoad(Test):
    def test_load(self):
        t = self.connect_as_admin()
        t.write('asetmaxplayer 2048\n')
        t.write('asetmaxguest 2043\n')
        self.close(t)

        self.finished = defer.Deferred()
        fact = protocol.ClientFactory()
        fact.protocol = TestProtocol
        fact.tester = self
        fact.num_done = 0
        fact.error = 0
        fact.conns = []
        #fact.shut_down = self.shut_down
        self.factory = fact

        #for i in range(0, conn_count):
        #    reactor.connectTCP(host, int(port), fact, timeout=15)

        #reactor.callLater(15, self.print_status)
        # for some reason the reactor hangs when starting too many
        # connections at once, so stagger them
        assert(conn_count % 50 == 0)
        t = 0.0
        for i in range(0, conn_count, 50):
            reactor.callLater(t, self.startN, 50)
            t += 1.0

        '''# Let's go
        if not profile:
            reactor.run()
        else:
            cProfile.runctx('reactor.run()', globals(), locals())'''

        #self.finished.addCallback(self.shut_down)
        return self.finished

    def startN(self, n):
        for i in range(0, n):
            reactor.connectTCP(host, int(port), self.factory, timeout=15)

    def print_status(self):
        for c in self.factory.conns:
            if c.state == 'prompt':
                sys.stdout.write('*')
            elif c.state == 'login':
                sys.stdout.write('x')
            elif c.state == 'connectionMade':
                sys.stdout.write('c')
                sys.stdout.write('{%d}' % len(c.allData))
            else:
                sys.stdout.write('?')
        print

    def shut_down(self):
        print("shutting down %d conns" % len(self.factory.conns))
        for c in self.factory.conns[:]:
            c.quit()
        for c in self.factory.conns:
            self.assert_(c.state == 'connectionLost')
        self.assert_(self.factory.num_done == conn_count)
        self.assert_(len(self.factory.conns) == 0)
        reactor.callFromThread(reactor.stop)
        if self.factory.error:
            self.fail()

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
