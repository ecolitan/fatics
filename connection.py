import time
from twisted.internet.protocol import Protocol

import user
import command

connections = []

class connection(Protocol):
        def connectionMade(self):
                connections.append(self)
                f = open("messages/welcome.txt")
                self.transport.write(f.read())
                self.login()

        def login(self):
                self.dataReceived = self.dataReceivedLogin
                f = open("messages/login.txt")
                self.transport.write(f.read())
                self.transport.write("login: ")

        def connectionLost(self, reason):
                try:
                        if self.user.is_online:
                                self.user.log_out()
                except AttributeError:
                        pass
                connections.remove(self)

        def dataReceivedLogin(self, data):
                name = data.strip()
                try:
                        self.user = user.find.by_name_for_login(name, self)
                except user.UsernameException as e:
                        self.write('\n' + e.reason + '\n')
                else:
                        self.dataReceived = self.dataReceivedPasswd
        
        def dataReceivedPasswd(self, data):
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
                                self.transport.write('\n\n**** Invalid password! ****\n\n')
                                self.login()

                assert(self.dataReceived != self.dataReceivedPasswd)

        def prompt(self):
                self.user.log_in()
                self.transport.write('fics% ')
                self.dataReceived = self.dataReceivedLoggedIn

        def dataReceivedLoggedIn(self, data):
                try:
                        command.handle_command(data.strip(), self)
                except command.QuitException:
                        self.transport.loseConnection()
                self.write('fics% ')
        
        def write(self, s):
                self.transport.write(s)
                
# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent ft=python
