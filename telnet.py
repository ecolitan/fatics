# Copyright (C) 2010 Wil Mahan <wmahan at gmail.com>

""" Telnet protocol implementation. """

"""The original FICS server supports a very limited subset of the telnet
protocol.  Since the the goal is to be compatible with FICS clients,
followed the server and not the RFC."""

from zope.interface import implements
from twisted.internet import protocol, interfaces
from twisted.python import log

# telnet codes
ECHO = chr(1)
TM = chr(6) # timing mark
# Note that we violate RFC 854, which says: "On a host that never sends the
# Telnet command Go Ahead (GA), the Telnet Server MUST attempt to negotiate
# the Suppress Go Ahead option...." We only send WILL SGA in response to
# DO SGA from the client.
SGA = chr(3) # supress go-ahead
IP = chr(244) # interrupt process
AYT = chr(246) # are you there?
EL = chr(248) # erase line
WILL = chr(251)
WONT = chr(252)
DO = chr(253)
DONT = chr(254)
IAC = chr(255) # interpret as command

BS = chr(8) # backspace

class Telnet(protocol.Protocol):
    """
    @ivar commandMap: A mapping of bytes to callables.  When a
    telnet command is received, the command byte (the first byte
    after IAC) is looked up in this dictionary.  If a callable is
    found, it is invoked with the argument of the command, or None
    if the command takes no argument.  Values should be added to
    this dictionary if commands wish to be handled.  By default,
    only WILL, WONT, DO, and DONT are handled.  These should not
    be overridden, as this class handles them correctly and
    provides an API for interacting with them.

    @ivar options: A mapping of option bytes to their current
    state.  This state is likely of little use to user code.
    Changes should not be made to it.

    @ivar state: A string indicating the current parse state.  It
    can take on the values "data", "escaped", "command", "newline",
    "subnegotiation", and "subnegotiation-escaped".  Changes
    should not be made to it.

    @ivar transport: This protocol's transport object.
    """

    # One of a lot of things
    state = 'data'

    def __init__(self):
        self.options = {}
        self.commandMap = {
            WILL: self.telnet_WILL,
            WONT: self.telnet_WONT,
            DO: self.telnet_DO,
            DONT: self.telnet_DONT}

    def _write(self, bytes):
        self.transport.write(bytes)

    def _do(self, option):
        self._write(IAC + DO + option)

    def _dont(self, option):
        self._write(IAC + DONT + option)

    def _will(self, option):
        self._write(IAC + WILL + option)

    def _wont(self, option):
        self._write(IAC + WONT + option)

    def will(self, option):
        """Indicate our willingness to enable an option.
        """
        self._will(option)

    def wont(self, option):
        """Indicate we are not willing to enable an option.
        """
        self._wont(option)

    def do(self, option):
        self._do(option)

    def dont(self, option):
        self._dont(option)

    def dataReceived(self, data):
        appDataBuffer = []

        for b in data:
            if self.state == 'data':
                if b == IAC:
                    self.state = 'escaped'
                elif b == '\r':
                    self.state = 'newline'
                else:
                    appDataBuffer.append(b)
            elif self.state == 'escaped':
                if b == IAC:
                    appDataBuffer.append(b)
                    self.state = 'data'
                elif b in (IP, AYT, EL):
                    self.state = 'data'
                    if appDataBuffer:
                        self.applicationDataReceived(''.join(appDataBuffer))
                        del appDataBuffer[:]
                    self.commandReceived(b, None)
                elif b in (WILL, WONT, DO, DONT):
                    self.state = 'command'
                    self.command = b
                else:
                    raise ValueError("Stumped", b)
            elif self.state == 'command':
                self.state = 'data'
                command = self.command
                del self.command
                if appDataBuffer:
                    self.applicationDataReceived(''.join(appDataBuffer))
                    del appDataBuffer[:]
                self.commandReceived(command, b)
            elif self.state == 'newline':
                self.state = 'data'
                if b == '\n':
                    appDataBuffer.append('\n')
                elif b == '\0':
                    appDataBuffer.append('\r')
                elif b == IAC:
                    # IAC isn't really allowed after \r, according to the
                    # RFC, but handling it this way is less surprising than
                    # delivering the IAC to the app as application data. 
                    # The purpose of the restriction is to allow terminals
                    # to unambiguously interpret the behavior of the CR
                    # after reading only one more byte.  CR LF is supposed
                    # to mean one thing (cursor to next line, first column),
                    # CR NUL another (cursor to first column).  Absent the
                    # NUL, it still makes sense to interpret this as CR and
                    # then apply all the usual interpretation to the IAC.
                    appDataBuffer.append('\r')
                    self.state = 'escaped'
                else:
                    appDataBuffer.append('\r' + b)
            else:
                raise ValueError("How'd you do this?")

        if appDataBuffer:
            self.applicationDataReceived(''.join(appDataBuffer))


    def connectionLost(self, reason):
        pass

    def applicationDataReceived(self, bytes):
        """Called with application-level data.
        """

    def commandReceived(self, command, argument):
        cmdFunc = self.commandMap.get(command)
        if cmdFunc:
            cmdFunc(argument)

    def telnet_WILL(self, option):
        pass

    def telnet_WONT(self, option):
        pass

    def telnet_DO(self, option):
        if option == TM:
                self._will(TM)
        elif option == SGA:
                self._will(SGA)

    def telnet_DONT(self, option):
        pass


class ProtocolTransportMixin:
    def write(self, bytes):
        self.transport.write(bytes.replace('\n', '\r\n'))

    def writeSequence(self, seq):
        self.transport.writeSequence(seq)

    def loseConnection(self):
        self.transport.loseConnection()

    def getHost(self):
        return self.transport.getHost()

    def getPeer(self):
        return self.transport.getPeer()

class TelnetTransport(Telnet, ProtocolTransportMixin):
    """
    @ivar protocol: An instance of the protocol to which this
    transport is connected, or None before the connection is
    established and after it is lost.

    @ivar protocolFactory: A callable which returns protocol instances
    which provide L{ITelnetProtocol}.  This will be invoked when a
    connection is established.  It is passed *protocolArgs and
    **protocolKwArgs.

    @ivar protocolArgs: A tuple of additional arguments to
    pass to protocolFactory.

    @ivar protocolKwArgs: A dictionary of additional arguments
    to pass to protocolFactory.
    """

    disconnecting = False

    protocolFactory = None
    protocol = None

    def __init__(self, protocolFactory=None, *a, **kw):
        Telnet.__init__(self)
        if protocolFactory is not None:
            self.protocolFactory = protocolFactory
            self.protocolArgs = a
            self.protocolKwArgs = kw

    def connectionMade(self):
        if self.protocolFactory is not None:
            self.protocol = self.protocolFactory(*self.protocolArgs, **self.protocolKwArgs)
            try:
                factory = self.factory
            except AttributeError:
                pass
            else:
                self.protocol.factory = factory
            self.protocol.makeConnection(self)

    def connectionLost(self, reason):
        Telnet.connectionLost(self, reason)
        if self.protocol is not None:
            try:
                self.protocol.connectionLost(reason)
            finally:
                del self.protocol

    def unhandledSubnegotiation(self, command, bytes):
        self.protocol.unhandledSubnegotiation(command, bytes)

    def applicationDataReceived(self, bytes):
        self.protocol.dataReceived(bytes)

    def write(self, data):
        ProtocolTransportMixin.write(self, data.replace('\xff','\xff\xff'))

# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent ft=python
