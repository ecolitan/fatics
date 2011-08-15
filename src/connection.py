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

import time
import re
import twisted.internet.interfaces

from twisted.protocols import basic
from twisted.internet import reactor
from zope.interface import implements

import telnet
import command_parser
import lang

from config import config
from db import db
from timeseal import timeseal, REPLY as TIMESEAL_REPLY
from session import Session
from login import login

# the set of users we have sent messages to and to whom we should
# thefore send prompts
written_users = set()
def send_prompts():
    for u in written_users:
        if u.is_online:
            u.send_prompt()
    written_users.clear()
    assert(not written_users)


class Connection(basic.LineReceiver):
    implements(twisted.internet.interfaces.IProtocol)
    # the telnet transport changes all '\r\n' to '\n',
    # so we can just use '\n' here
    delimiter = '\n'
    MAX_LENGTH = 1024
    state = 'prelogin'
    user = None
    logged_in_again = False
    buffer_output = False
    ivar_pat = re.compile(r'%b([01]{32})')
    timeout_check = None

    def connectionMade(self):
        lang.langs['en'].install(names=['ngettext'])
        self.session = Session(self)
        if self.transport.getHost().port == config.zipseal_port:
            self.session.use_zipseal = True
            self.transport.encoder = timeseal.compress_zipseal
            self.session.check_for_timeseal = False
        self.factory.connections.append(self)
        self.write(db.get_server_message('welcome'))
        self.login()
        self.session.login_last_command = time.time()
        self.ip = self.transport.getPeer().host
        self.timeout_check = reactor.callLater(config.login_timeout, self.login_timeout)

    def login_timeout(self):
        assert(self.state in ['login', 'passwd'])
        self.timeout_check = None
        self.write(_("\n**** LOGIN TIMEOUT ****\n"))
        self.loseConnection('login timeout')

    def idle_timeout(self, mins):
        assert(self.state in ['prompt'])
        self.write(_("\n**** Auto-logout because you were idle more than %d minutes. ****\n") % mins)
        self.loseConnection('idle timeout')

    def login(self):
        self.state = 'login'
        self.write(db.get_server_message('login'))
        if self.transport.compatibility:
            # the string "freechess.org" must appear somewhere in this message;
            # otherwise, Babs will refuse to connect
            self.write('You are connected to the backwards-compatibility port for old FICS clients.\nYou will not be able to use zipseal or international characters.\nThis server is not endorsed by freechess.org.\n\n')
        self.write("login: ")

    def lineReceived(self, line):
        #print '((%s,%s))\n' % (self.state, repr(line))
        if self.session.use_timeseal:
            (t, line) = timeseal.decode_timeseal(line)
        elif self.session.use_zipseal:
            (t, line) = timeseal.decode_zipseal(line)
        else:
            t = None
        if t == 0:
            self.write('timeseal error\n')
            self.loseConnection('timeseal error')
            return
        self.session.timeseal_last_timestamp = t
        if self.state:
            getattr(self, "lineReceived_" + self.state)(line)

    def lineReceived_quitting(self, line):
        """ Shouldn't happen normally. """
        pass

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
                # we don't detect zipseal here, because we use
                # the port number to detect it
            # no timeseal; continue

        m = self.ivar_pat.match(line)
        if m:
            self.session.set_ivars_from_str(m.group(1))
            return
        name = line.strip()
        # hide password
        self.transport.will(telnet.ECHO)
        self.claimed_user = login.get_user(name, self)
        if self.claimed_user:
            self.state = 'passwd'
        else:
            if self.state != 'quitting':
                self.transport.wont(telnet.ECHO)
                self.write("\nlogin: ")

    def lineReceived_passwd(self, line):
        self.timeout_check.cancel()
        self.timeout_check = reactor.callLater(config.login_timeout, self.login_timeout)
        self.session.login_last_command = time.time()
        self.transport.wont(telnet.ECHO)
        self.write('\n')
        if self.claimed_user.is_guest:
            # ignore whatever was entered in place of a password
            self.prompt()
        else:
            passwd = line.strip()
            if len(passwd) == 0:
                self.login()
            elif self.claimed_user.check_passwd(passwd):
                self.prompt()
            else:
                self.write('\n**** Invalid password! ****\n\n')
                self.login()
        assert(self.state != 'passwd')

    def prompt(self):
        self.user = self.claimed_user
        self.timeout_check.cancel()
        self.timeout_check = None
        self.user.log_on(self)
        assert(self.user.is_online)
        written_users.add(self.user)
        self.state = 'prompt'
        send_prompts()

    def lineReceived_prompt(self, line):
        if line == TIMESEAL_REPLY:
            self.session.pong(self.session.timeseal_last_timestamp)
            return

        lang.langs[self.user.vars['lang']].install(names=['ngettext'])
        written_users.clear()
        written_users.add(self.user)
        try:
            command_parser.parser.parse(line, self)
        finally:
            send_prompts()

    def loseConnection(self, reason):
        self.state = 'quitting'
        if self.timeout_check:
            self.timeout_check.cancel()
            self.timeout_check = None
        if reason == 'logged in again':
            # As a special case, we don't want to remove a user
            # from the online list if we are losing this connection
            # because the same user is logging in from another connection.
            # This approach is necessary because when the user re-logs in,
            # we don't want to have to wait for the first connection
            # to finish closing before logging in.
            self.logged_in_again = True
        # We prefer to call log_off() before the connection is closed so
        # we can print messages such as forfeit by disconnection,
        # but if the user disconnects abruptly then log_off() will be
        # called in connectionLost() instead.
        if self.user and self.user.is_online:
            self.user.log_off()
        self.transport.loseConnection()
        if reason == 'quit':
            #timeseal.print_stats()
            self.write(db.get_server_message('logout'))

    def connectionLost(self, reason):
        basic.LineReceiver.connectionLost(self, reason)
        try:
            if self.user.is_online:
                if self.logged_in_again:
                    self.logged_in_again = False
                else:
                    # abrupt disconnection
                    self.user.log_off()
        except AttributeError:
            # never logged in
            pass
        self.factory.connections.remove(self)

    def write(self, s):
        if self.buffer_output:
            self.output_buffer += s
        else:
            self.transport.write(s)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
