#!/usr/bin/env python
from twisted.internet.protocol import Factory, Protocol
from twisted.internet import reactor

PORT = 5000

class SendContent(Protocol):
        def connectionMade(self):
                self.transport.write(self.factory.text)

        def dataReceived(self, data):
                print(data)
                self.transport.loseConnection()
                

class SendContentFactory(Factory):
        protocol = SendContent
        def __init__(self, text=None):
                if text is None:
                        text = """Hello, how are you my friend? Feeling fine? Good!"""
                self.text = text

reactor.listenTCP(PORT, SendContentFactory())
reactor.run()

# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent
