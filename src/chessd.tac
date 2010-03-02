"""
a twisted application for chessd
"""

import os
import sys
from twisted.application import service, internet
from twisted.internet.protocol import ServerFactory
from twisted.internet import reactor
import gettext

langs = {
    'en': gettext.NullTranslations(),
    'es': gettext.translation('chessd', languages=['es'], localedir='./locale'),
    'compat': gettext.translation('chessd', languages=['compat'], localedir='./locale')
}
#gettext.install('chessd', './locale')

from config import config
import telnet
import connection
import var

if os.geteuid() == 0:
    sys.path.append('.')

class IcsFactory(ServerFactory):
    connections = []
    langs = langs
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
if os.geteuid() == 0:
    service = getService(23)
    service.setServiceParent(application)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent ft=python
