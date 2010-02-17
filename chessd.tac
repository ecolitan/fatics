"""
a twisted application for chessd
"""

import os

from twisted.application import service, internet
from twisted.internet.protocol import ServerFactory
from twisted.internet import reactor

import gettext
import sys

import telnet
import connection

gettext.install('interface', './locale', unicode=False)

if os.geteuid() == 0:
        sys.path.append('.')

PORT = 5000

class IcsFactory(ServerFactory):
        def buildProtocol(self, addr):
                return telnet.TelnetTransport(connection.Connection)

def getService(port):
        """
        Return a service suitable for creating an application object.
        """
        return internet.TCPServer(port, IcsFactory())

application = service.Application("chessd")

service = getService(5000)
service.setServiceParent(application)
if os.geteuid() == 0:
        service = getService(23)
        service.setServiceParent(application)

# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent ft=python
