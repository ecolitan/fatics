# You can run this .tac file directly with:
#    twistd -ny service.tac

"""

"""

from twisted.application import service, internet
from twisted.internet.protocol import Factory
from twisted.internet import reactor
from twisted.conch.telnet import TelnetTransport

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
#try:
#        service = getService(23)
#        service.setServiceParent(application)
#except twisted.internet.error.CannotListenError:
#        pass

# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent ft=python
