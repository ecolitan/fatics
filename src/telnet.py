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

# Copyright (C) 2010 Wil Mahan <wmahan at gmail.com>

# Loosely based on conch.telnet from twisted.  Here is the
# copyright header for that code:
#       Copyright (c) 2001-2007 Twisted Matrix Laboratories.
#       See LICENSE for details.
#       @author: Jp Calderone
#

""" Telnet protocol implementation. """

"""The original FICS server supports a very limited subset of the telnet
protocol.  Since the the goal is to be compatible with FICS clients,
followed the server and not the RFC."""

from zope.interface import implements
from twisted.internet import protocol, interfaces

import utf8

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

class TelnetTransport(protocol.Protocol):
    implements(interfaces.ITransport)
    protocolFactory = None
    protocol = None
    disconnecting = False
    encoder = None

    def __init__(self, protocolFactory=None, *a, **kw):
        self.commandMap = {
            WILL: self.telnet_WILL,
            WONT: self.telnet_WONT,
            DO: self.telnet_DO,
            DONT: self.telnet_DONT,
            IP: self.telnet_IP,
            AYT: self.telnet_AYT}
        self.state = 'data'
        if protocolFactory is not None:
            self.protocolFactory = protocolFactory
            self.protocolArgs = a
            self.protocolKwArgs = kw

    def _write(self, bytes):
        if self.encoder is not None:
            bytes = self.encoder(bytes)
        self.transport.write(bytes)

    def do(self, option):
        self._write(IAC + DO + option)

    def dont(self, option):
        self._write(IAC + DONT + option)

    def will(self, option):
        self._write(IAC + WILL + option)

    def wont(self, option):
        self._write(IAC + WONT + option)

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
                    self.state = 'data'
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
                raise ValueError("should not happen: unknown state")

        if appDataBuffer:
            self.applicationDataReceived(''.join(appDataBuffer))


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
            self.will(TM)
        elif option == SGA:
            self.will(SGA)

    def telnet_DONT(self, option):
        pass

    def telnet_IP(self, option):
        self.loseConnection()

    def telnet_AYT(self, option):
        pass

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
        if self.protocol is not None:
            try:
                self.protocol.connectionLost(reason)
            finally:
                del self.protocol

    def applicationDataReceived(self, bytes):
        self.protocol.dataReceived(bytes)

    def _escape(self, data):
        data = data.replace('''\xff''', '''\xff\xff''')
        if self.compatibility:
            #data = data.decode('ascii','replace').replace(u'\ufffd', '_')
            data = utf8.utf8_to_ascii(data)
            data = data.replace('\n', '\n\r')
        else:
            data = data.replace('\n', '\r\n')
        return data

    def write(self, data):
        data = self._escape(data)
        self._write(data)

    def writeSequence(self, seq):
        self.transport.writeSequence(seq)

    def loseConnection(self):
        self.transport.loseConnection()

    def getHost(self):
        return self.transport.getHost()

    def getPeer(self):
        return self.transport.getPeer()

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
