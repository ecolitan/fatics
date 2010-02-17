import time
from twisted.protocols import basic
import twisted.internet.interfaces
from zope.interface import implements

import telnet
import user
import command
from timeseal import timeseal
from session import Session
from login import login

connections = []

class Connection(basic.LineReceiver):
        implements(twisted.internet.interfaces.IProtocol)
        # the telnet transport changes all '\n' to 
        # '\r\n', so we can just use '\n' here
        delimiter = '\n'
        MAX_LENGTH = 1024
        ics_state = 'initial'
        user = None

        def connectionMade(self):
                self.transport.commandMap[telnet.IP] = self.loseConnection
                connections.append(self)
                f = open("messages/welcome.txt")
                self.write(f.read())
                self.login()
                self.session = Session(self)

        def login(self):
                self.ics_state = 'login'
                f = open("messages/login.txt")
                self.write(f.read())
                self.write("login: ")

        def lineReceived(self, line):
                #print '((%s,%s))\n' % (self.ics_state, repr(line))
                if self.session.use_timeseal:
                        (t, line) = timeseal.decode(line)
                if self.ics_state:
                        getattr(self, "lineReceived_" + self.ics_state)(line)

        def connectionLost(self, reason):
                basic.LineReceiver.connectionLost(self, reason)
                try:
                        if self.user.is_online:
                                self.user.log_out()
                        self.session.close()
                except AttributeError:
                        pass
                connections.remove(self)
        
        def lineReceived_initial(self):
                pass

        def lineReceived_login(self, line):
                if self.session.check_for_timeseal:
                        self.session.check_for_timeseal = False
                        (t, dec) = timeseal.decode(line)
                        if t != 0 and dec[0:10] == 'TIMESTAMP|':
                                self.session.use_timeseal = True
                                return
                name = line.strip()
                self.user = login.get_user(name, self)
                if self.user:
                        self.transport.will(telnet.ECHO)
                        self.ics_state = 'passwd'
                else:
                        self.write("login: ")
        
        def lineReceived_passwd(self, line):
                self.transport.wont(telnet.ECHO)
                self.write('\n')
                if self.user.is_guest:
                        # ignore whatever was entered in place of a password
                        self.prompt()
                else:
                        passwd = line.strip()
                        if len(passwd) == 0:
                                self.login()
                        elif self.user.check_passwd(passwd):
                                self.prompt()
                        else:
                                self.write('\n\n**** Invalid password! ****\n\n')
                                self.login()
                assert(self.ics_state != 'passwd')

        def prompt(self):
                self.user.log_in(self)
                self.write('fics% ')
                self.ics_state = 'online'

        def lineReceived_online(self, line):
                try:
                        command.parser.run(line, self)
                        self.write('fics% ')
                except command.QuitException:
                        f = open("messages/logout.txt")
                        self.write(f.read())
                        self.loseConnection('quit')

        def loseConnection(self, reason):
                if self.user and self.user.is_online:
                        self.user.log_out()
                self.transport.loseConnection()
        
        def write(self, s):
                self.transport.write(s)
                
# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent ft=python
