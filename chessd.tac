# You can run this .tac file directly with:
#    twistd -ny service.tac

"""

"""

from twisted.application import service, internet
from twisted.internet.protocol import Factory
from twisted.internet import reactor

import connection

PORT = 5000

class IcsFactory(Factory):
        protocol = connection.connection

def getService():
    """
    Return a service suitable for creating an application object.
    """
    return internet.TCPServer(5000, IcsFactory())

# this is the core part of any tac file, the creation of the root-level
# application object
application = service.Application("chessd")

# attach the service to its parent application
service = getService()
service.setServiceParent(application)

# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent ft=python
