"""
a twisted application for chessd
"""

import os
import sys
from twisted.application import service, internet
from twisted.internet.protocol import ServerFactory
from twisted.internet import epollreactor, task

sys.path.insert(0, 'src/')

# add a builtin to mark strings for translation that should not
# automatically be translated dynamically.
import __builtin__
# dynamically translated messages
__builtin__.__dict__['N_'] = lambda s: s
# admin messages
__builtin__.__dict__['A_'] = lambda s: s

from config import config
import telnet
import connection
import var
import clock

if os.geteuid() == 0:
    sys.path.append('.')

class IcsFactory(ServerFactory):
    def __init__(self):
        #ServerFactory.__init__(self)
        self.lc = task.LoopingCall(clock.heartbeat)
        self.lc.start(10)

    connections = []
    def buildProtocol(self, addr):
        conn = telnet.TelnetTransport(connection.Connection)
        conn.factory = self
        return conn

def getService(port):
    """
    Return a service suitable for creating an application object.
    """
    return internet.TCPServer(port, IcsFactory())

application = service.Application("chessd")

service = getService(config.port)
service.setServiceParent(application)
service = getService(config.zipseal_port)
service.setServiceParent(application)
if os.geteuid() == 0:
    service = getService(23)
    service.setServiceParent(application)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent ft=python
