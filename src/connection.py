import time
import re
from twisted.protocols import basic
import twisted.internet.interfaces
from twisted.internet import reactor
from zope.interface import implements

import telnet
import command
import command_parser
import lang
from config import config
from timeseal import timeseal
from session import Session
from login import login

class Connection(basic.LineReceiver):
    implements(twisted.internet.interfaces.IProtocol)
    # the telnet transport changes all '\r\n' to '\n',
    # so we can just use '\n' here
    delimiter = '\n'
    MAX_LENGTH = 1024
    state = 'prelogin'
    user = None
    logged_in_again = False
    ivar_pat = re.compile(r'%b([01]{32})')

    def connectionMade(self):
        lang.langs['en'].install(names=['ngettext'])
        self.session = Session(self)
        if self.transport.getHost().port == config.zipseal_port:
            self.session.use_zipseal = True
            self.session.check_for_timeseal = False
        self.factory.connections.append(self)
        self.write(config.welcome_msg)
        self.login()
        self.session.login_last_command = time.time()
        self.ip = self.transport.getPeer().host
        self.timeout_check = reactor.callLater(config.login_timeout, self.login_timeout)

    def login_timeout(self):
        assert(self.state in ['login', 'passwd'])
        self.write(_("\n**** LOGIN TIMEOUT ****\n"))
        self.loseConnection('login timeout')

    def login(self):
        #assert(self.state == 'login')
        self.state = 'login'
        self.write(config.login_msg)
        self.write("login: ")

    def lineReceived(self, line):
        #print '((%s,%s))\n' % (self.state, repr(line))
        if self.session.use_timeseal:
            (t, line) = timeseal.decode_timeseal(line)
            assert(t != 0)
        elif self.session.use_zipseal:
            (t, line) = timeseal.decode_zipseal(line)
            assert(t != 0)
        if self.state:
            getattr(self, "lineReceived_" + self.state)(line)

    def lineReceived_login(self, line):
        self.timeout_check.cancel()
        self.timeout_check = reactor.callLater(config.login_timeout, self.login_timeout)
        self.session.login_last_command = time.time()
        if self.session.check_for_timeseal:
            self.session.check_for_timeseal = False
            (t, dec) = timeseal.decode_timeseal(line)
            if t != 0:
                if dec[0:10] == 'TIMESTAMP|':
                    self.session.use_timeseal = True
                    return
                elif dec[0:10] == 'TIMESEAL2|':
                    self.session.use_timeseal = True
                    return
            '''(t, dec) = timeseal.decode_zipseal(line)
            if t != 0:
                if dec[0:8] == 'zipseal|':
                    self.write('ZIPSEAL\n')
                    self.session.use_zipseal = True
                    return'''
            # no timeseal; continue

        m = self.ivar_pat.match(line)
        if m:
            self.session.set_ivars_from_str(m.group(1))
            return
        name = line.strip()
        self.user = login.get_user(name, self)
        if self.user:
            self.transport.will(telnet.ECHO)
            self.state = 'passwd'
        else:
            self.write("login: ")

    def lineReceived_passwd(self, line):
        self.timeout_check.cancel()
        self.timeout_check = reactor.callLater(config.login_timeout, self.login_timeout)
        self.session.login_last_command = time.time()
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
                self.write('\n**** Incorrect password ****\n\n')
                self.login()
        assert(self.state != 'passwd')

    def prompt(self):
        self.timeout_check.cancel()
        self.user.log_on(self)
        assert(self.user.is_online)
        self.user.write_prompt(None)
        self.state = 'online'

    def lineReceived_online(self, line):
        lang.langs[self.user.vars['lang']].install(names=['ngettext'])
        try:
            command_parser.parser.run(line, self)
            self.user.write_prompt(None)
        except command.QuitException:
            self.loseConnection('quit')

    def loseConnection(self, reason):
        if reason == 'logged in again':
            self.logged_in_again = True
        if self.user and self.user.is_online:
            self.user.log_off()
        self.transport.loseConnection()
        if reason == 'quit':
            self.write(config.logout_msg)

    def connectionLost(self, reason):
        basic.LineReceiver.connectionLost(self, reason)
        try:
            # as a special case, we don't want to remove our user name
            # from the online list if we are losing this connection
            # because the same user is logging in from another connection
            if self.user.is_online and not self.logged_in_again:
                self.user.log_off()
            self.session.close()
        except AttributeError:
            pass
        self.factory.connections.remove(self)


    def write(self, s):
        if self.session.use_zipseal:
            s = self.transport.escape(s)
            self.transport.write(timeseal.compress_zipseal(s), raw=True)
        else:
            self.transport.write(s)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
