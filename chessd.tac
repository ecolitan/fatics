"""
a twisted application for chessd
"""

import os

from twisted.application import service, internet
from twisted.internet.protocol import Factory
from twisted.internet import reactor
from twisted.conch.telnet import TelnetTransport

import sys
if os.geteuid() == 0:
        sys.path.append('.')
import ics_protocol

PORT = 5000

class IcsFactory(Factory):
        def buildProtocol(self, addr):
                return TelnetTransport(ics_protocol.IcsProtocol)

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
