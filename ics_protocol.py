import time
from twisted.conch.telnet import TelnetProtocol, ECHO
from twisted.protocols import basic

import user
import command

connections = []

class IcsProtocol(basic.LineReceiver, TelnetProtocol):
        # the telnet transport changes all '\n' to 
        # '\r\n', so we can just use '\n' here
        delimiter = '\n'
        MAX_LENGTH = 1024
        def connectionMade(self):
                connections.append(self)
                f = open("messages/welcome.txt")
                self.write(f.read())
                self.login()

        def login(self):
                self.lineReceived = self.lineReceivedLogin
                f = open("messages/login.txt")
                self.write(f.read())
                self.write("login: ")

        def connectionLost(self, reason):
                basic.LineReceiver.connectionLost(self, reason)
                TelnetProtocol.connectionLost(self, reason)
                try:
                        if self.user.is_online:
                                self.user.log_out()
                except AttributeError:
                        pass
                connections.remove(self)

        def lineReceivedLogin(self, data):
                name = data.strip()
                try:
                        self.user = user.find.by_name_for_login(name, self)
                except user.UsernameException as e:
                        self.write('\n' + e.reason + '\n')
                        self.write("login: ")
                else:
                        self.transport.will(ECHO)
                        self.lineReceived = self.lineReceivedPasswd
        
        def lineReceivedPasswd(self, data):
                self.transport.wont(ECHO)
                if self.user.is_guest:
                        # ignore whatever was entered in place of a password
                        self.prompt()
                else:
                        passwd = data.strip()
                        if len(passwd) == 0:
                                self.login()
                        elif self.user.check_passwd(passwd):
                                self.prompt()
                        else:
                                self.write('\n\n**** Invalid password! ****\n\n')
                                self.login()

                assert(self.lineReceived != self.lineReceivedPasswd)

        def prompt(self):
                self.user.log_in()
                self.write('fics% ')
                self.lineReceived = self.lineReceivedLoggedIn

        def lineReceivedLoggedIn(self, data):
                try:
                        command.handle_command(data.strip(), self)
                except command.QuitException:
                        self.transport.loseConnection()
                self.write('fics% ')
        
        def write(self, s):
                self.transport.write(s)
                
# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent ft=python
