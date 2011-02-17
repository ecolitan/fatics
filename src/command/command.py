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

import re

import user
import trie
import admin
import game
import history
import speed_variant
import online
import time_format
import channel

from server import server
from db import db, DeleteError
from config import config

class CommandList(object):
    def __init__(self):
        self.cmds = trie.Trie()
        self.admin_cmds = trie.Trie()
command_list = CommandList()

# parameter format (taken from Lasker)
# w - a word
# o - an optional word
# d - integer
# p - optional integer
# i - word or integer
# n - optional word or integer
# s - string to end
# t - optional string to end
# lowercase <-> case-insensitive

class Command(object):
    def __init__(self, name, param_str, admin_level):
        assert(hasattr(self, 'run'))
        self.name = name
        self.param_str = param_str
        self.admin_level = admin_level
        command_list.admin_cmds[name] = self
        if admin_level <= admin.Level.user:
            command_list.cmds[name] = self

    def help(self, conn):
        conn.write("help for %s\n" % self.name)

    def usage(self, conn):
        conn.write("Usage: TODO for %s\n" % self.name)

class ics_command(object):
    def __init__(self, name, param_str, admin_level=admin.Level.user):
        self.name = name
        self.param_str = param_str
        self.admin_level = admin_level

    def __call__(self, f):
        # just a check that the naming convention is correct
        import inspect
        assert(inspect.getmro(f)[0].__name__ == self.name.capitalize())
        # instantiate the decorated class at decoration time
        f(self.name, self.param_str, self.admin_level)
        def wrapped_f(*args):
            raise RuntimeError('command objects should not be instantiated directly')
        return wrapped_f

def requires_registration(f):
    def check_reg(self, args, conn):
        if conn.user.is_guest:
            conn.write(_("Only registered players can use the %s command.\n") % self.name)
        else:
            f(self, args, conn)
    return check_reg

@ics_command('alias', 'oT', admin.Level.user)
class Alias(Command):
    def run(self, args, conn):
        if args[0] is None:
            # show list of aliases
            if len(conn.user.aliases) == 0:
                conn.write(_('You have no aliases.\n'))
            else:
                conn.write(_('Aliases:\n'))
                for (k, v) in conn.user.aliases.iteritems():
                    conn.write(_("%s -> %s\n") % (k, v))
            return

        aname = args[0]
        assert(aname == aname.lower())
        if not 1 <= len(aname) < 16:
            conn.write(_("Alias names may not be more than 15 characters long.\n"))
            return

        if aname in ['quit', 'unalias']:
            conn.write(_('You cannot use "%s" as an alias.\n') % aname)

        if args[1] is None:
            # show alias value
            if aname not in conn.user.aliases:
                conn.write(_('You have no alias named "%s".\n') % aname)
            else:
                conn.write(_("%s -> %s\n") % (aname,
                    conn.user.aliases[aname]))
            return

        # set alias value
        was_set = aname in conn.user.aliases
        conn.user.set_alias(aname, args[1])
        if was_set:
            conn.write(_('Alias "%s" changed.\n') % aname)
        else:
            conn.write(_('Alias "%s" set.\n') % aname)

@ics_command('games', 'o', admin.Level.user)
class Games(Command):
    def run(self, args, conn):
        if not game.games.values():
            conn.write(_('There are no games in progress.\n'))
            return
        if args[0] is not None:
            conn.write('TODO: games PARAM\n')
        count = 0
        for g in game.games.values():
            count += 1
        conn.write(ngettext('  %(count)d game displayed (of %(total)3d in progress).\n', '  %(count)d games displayed (of %(total)d in progress).\n', count) % {'count': count, 'total': len(game.games)})

@ics_command('help', 'o', admin.Level.user)
class Help(Command):
    def run(self, args, conn):
        if args[0] in ['license', 'license', 'copying', 'copyright']:
            conn.write(server.get_license())
            return
        if conn.user.admin_level > admin.level.user:
            cmds = [c.name for c in command_list.admin_cmds.itervalues()]
        else:
            cmds = [c.name for c in command_list.cmds.itervalues()]
        conn.write('This server is under development.\n\nRecognized commands: %s\n' % ' '.join(cmds))

@ics_command('limits', '')
class Limits(Command):
    def run(self, args, conn):
        conn.write(_('Current hardcoded limits:\n'))
        conn.write(_('  Server:\n'))
        conn.write(_('    Channels: %d\n') % channel.CHANNEL_MAX)
        conn.write(_('    Players: %d\n') % config.maxplayer)
        conn.write(_('    Connections: %(umax)d users (+ %(amax)d admins)\n') %
            {'umax': config.maxplayer - config.admin_reserve,
                'amax': config.admin_reserve})

@ics_command('password', 'WW')
class Password(Command):
    def run(self, args, conn):
        if conn.user.is_guest:
            conn.write(_("Setting a password is only for registered players.\n"))
        else:
            [oldpass, newpass] = args
            if not conn.user.check_passwd(oldpass):
                conn.write(_("Incorrect password; password not changed!\n"))
            else:
                conn.user.set_passwd(newpass)
                conn.write(_("Password changed to %s.\n") % ('*' * len(newpass)))

@ics_command('quit', '', admin.Level.user)
class Quit(Command):
    def run(self, args, conn):
        conn.loseConnection('quit')

@ics_command('unalias', 'w', admin.Level.user)
class Unalias(Command):
    def run(self, args, conn):
        aname = args[0]
        if not 1 <= len(aname) < 16:
            conn.write(_("Alias names may not be more than 15 characters long.\n"))
            return

        if aname not in conn.user.aliases:
            conn.write(_('You have no alias "%s".\n') % aname)
        else:
            conn.user.set_alias(aname, None)
            conn.write(_('Alias "%s" unset.\n') % aname)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
