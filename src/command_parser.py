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

class InternalException(Exception):
    pass
class BadCommandError(Exception):
    pass
class QuitException(Exception):
    pass

import alias
import utf8
import trie
import admin
from command import *
import timeseal


class CommandParser(object):
    command_re = re.compile(r'^(\S+)(?:\s+(.*))?$')
    def run(self, s, t, conn):
        s = s.strip()

        if s == timeseal.REPLY:
            if not conn.session.ping_sent:
                conn.write('protocol error: got reply without ping')
                conn.loseConnection('protocol error: got reply without ping')
            else:
                conn.session.ping_reply_time = t
            return

        if conn.session.games:
            if conn.session.games.primary().parse_move(s, t, conn):
                return

        if not utf8.checker.check_user_utf8(s):
            conn.write(_("Command ignored: invalid characters.\n"))
            return

        update_idle = True
        # previously the prefix '$' was used to not expand aliases
        # and '$$' was used to not update the idle time.  But these
        # options should really be orthogonal, so I made '$$' alone
        # expand aliaes. Now if you want the old behavior of neither
        # expanding aliases nor updating idle time, use '$$$'.
        if len(s) >= 2 and s[0:2] == '$$':
            s = s[2:].lstrip()
        else:
            conn.user.session.last_command_time = time.time()

        if len(s) == 0:
            # ignore blank line
            return

        if s[0] == '$':
            s = s[1:].lstrip()
        else:
            try:
                s = alias.alias.expand(s, alias.alias.system,
                    conn.user.aliases, conn.user)
            except alias.AliasError:
                conn.write(_("Command failed: There was an error expanding aliases.\n"))
                return

        if conn.user.admin_level > admin.Level.user:
            cmds = command.command_list.admin_cmds
        else:
            cmds = command.command_list.cmds

        cmd = None
        m = self.command_re.match(s)
        if m:
            word = m.group(1).lower()
            try:
                cmd = cmds[word]
            except KeyError:
                conn.write(_("%s: Command not found.\n") % word)
            except trie.NeedMore:
                matches = cmds.all_children(word)
                assert(len(matches) > 0)
                if len(matches) == 1:
                    cmd = matches[0]
                else:
                    conn.write(_("""Ambiguous command "%s". Matches: %s\n""") % (word, ' '.join([c.name for c in matches])))
            if cmd:
                try:
                    args = self.parse_args(m.group(2), cmd.param_str)
                    cmd.run(args, conn)
                except BadCommandError:
                    cmd.usage(conn)
        else:
            #conn.write(_("Command not found.\n"))
            assert(False)

    def parse_args(self, s, param_str):
        args = []
        for c in param_str:
            if c in ['d', 'i', 'w', 'W', 'f']:
                # required argument
                if s is None:
                    raise BadCommandError()
                else:
                    s = s.lstrip()
                    m = re.split(r'\s', s, 1)
                    assert(len(m) > 0)
                    param = m[0]
                    if len(param) == 0:
                        raise BadCommandError()
                    if c == c.lower():
                        param = param.lower()
                    if c in ['i', 'd']:
                        # integer or word
                        try:
                            param = int(param, 10)
                        except ValueError:
                            if c == 'd':
                                raise BadCommandError()
                    elif c == 'f':
                        try:
                            param = float(param)
                        except ValueError:
                            raise BadCommandError()
                    s = m[1] if len(m) > 1 else None
            elif c in ['o', 'n', 'p']:
                # optional argument
                if s is None:
                    param = None
                else:
                    s = s.lstrip()
                    m = re.split(r'\s', s, 1)
                    assert(len(m) > 0)
                    param = m[0].lower()
                    if len(param) == 0:
                        param = None
                        assert(len(m) == 1)
                    elif c in ['n', 'p']:
                        try:
                            param = int(param, 10)
                        except ValueError:
                            if c == 'p':
                                raise BadCommandError()
                    s = m[1] if len(m) > 1 else None
            elif c == 'S':
                # string to end
                if s is None or len(s) == 0:
                    raise BadCommandError()
                param = s
                s = None
            elif c == 'T' or c == 't':
                # optional string to end
                if s is None or len(s) == 0:
                    param = None
                else:
                    param = s
                    if c == 't':
                        param = param.lower()
                s = None
            else:
                raise InternalException()
            args.append(param)

        if not (s is None or re.match(r'^\s*$', s)):
            # extraneous data at the end
            raise BadCommandError()

        return args


parser = CommandParser()

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
