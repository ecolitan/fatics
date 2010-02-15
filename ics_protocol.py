import time
from twisted.conch import telnet
from twisted.protocols import basic

import user
import command
from timeseal import timeseal
from session import Session

connections = []

class IcsProtocol(basic.LineReceiver, telnet.TelnetProtocol):
        # the telnet transport changes all '\n' to 
        # '\r\n', so we can just use '\n' here
        delimiter = '\n'
        MAX_LENGTH = 1024
        ics_state = 'initial'

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
                print '((%s,%s))\n' % (self.ics_state, repr(line))
                if self.session.use_timeseal:
                        (t, line) = timeseal.decode(line)
                if self.ics_state:
                        getattr(self, "lineReceived_" + self.ics_state)(line)

        def connectionLost(self, reason):
                basic.LineReceiver.connectionLost(self, reason)
                telnet.TelnetProtocol.connectionLost(self, reason)
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
                        print 'checking for timeseal'
                        if t != 0 and dec[0:10] == 'TIMESTAMP|':
                                print 'enabled timeseal'
                                self.session.use_timeseal = True
                                return
                        else:
                                print 'disabled timeseal'
                name = line.strip()
                try:
                        self.user = user.find.by_name_for_login(name, self)
                except user.UsernameException as e:
                        self.write('\n' + e.reason + '\n')
                        self.write("login: ")
                else:
                        d = self.transport.will(telnet.ECHO)
                        self.ics_state = 'passwd'
        
        def lineReceived_passwd(self, line):
                if self.session.use_timeseal:
                        # timeseal interferes with us receiving confirmation
                        # that the client has disabled echo, so assume
                        # it was disabled
                        #s = self.transport.getOptionState(telnet.ECHO)
                        #s.us.negotiating = False
                        #s.us.state = 'yes'
                        self.transport.telnet_DO(telnet.ECHO)
                d = self.transport.wont(telnet.ECHO)
                if self.session.use_timeseal:
                        # see above
                        self.transport.telnet_DONT(telnet.ECHO)
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
                        command.handle_command(line, self)
                        self.write('fics% ')
                except command.QuitException:
                        f = open("messages/logout.txt")
                        self.write(f.read())
                        self.loseConnection('quit')

        def loseConnection(self, reason):
                self.transport.loseConnection()
        
        def write(self, s):
                self.transport.write(s)
                
# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent ft=python
