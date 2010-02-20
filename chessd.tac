"""
a twisted application for chessd
"""

import os

from twisted.application import service, internet
from twisted.internet.protocol import ServerFactory
from twisted.internet import reactor
import gettext
import sys

gettext.install('interface', './locale', unicode=False)

import telnet
import connection
import var

if os.geteuid() == 0:
        sys.path.append('.')

PORT = 5001

class IcsFactory(ServerFactory):
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

service = getService(PORT)
service.setServiceParent(application)
if os.geteuid() == 0:
        service = getService(23)
        service.setServiceParent(application)

# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent ft=python
