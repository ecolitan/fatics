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
import datetime
import re

import user
import trie
import admin
import var
import offer
import game
import history
import rating
import speed_variant

from timer import timer
from online import online
from reload import reload
from server import server
from command_parser import BadCommandError
from db import db, DeleteError

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

@ics_command('date', '', admin.Level.user)
class Date(Command):
    def run(self, args, conn):
        t = time.time()
        #conn.write(_("Local time     - %s\n") % )
        conn.write(_("Server time    - %s\n") % time.strftime("%a %b %e, %H:%M %Z %Y", time.localtime(t)))
        conn.write(_("GMT            - %s\n") % time.strftime("%a %b %e, %H:%M GMT %Y", time.gmtime(t)))

@ics_command('finger', 'ooo', admin.Level.user)
class Finger(Command):
    def run(self, args, conn):
        if args[0] is not None:
            u = user.find.by_prefix_for_user(args[0], conn, min_len=2)
        else:
            u = conn.user
        if u:
            conn.write(_('Finger of %s:\n\n') % u.get_display_name())

            if u.is_online:
                conn.write(_('On for: %s   Idle: %s\n') % (u.session.get_online_time(), u.session.get_idle_time()))
                if u.vars['silence']:
                    conn.write(_('%s is in silence mode.\n') % u.name)

                if u.session.game:
                    g = u.session.game
                    if g.gtype == game.PLAYED:
                        conn.write(_('(playing game %d: %s vs. %s)\n') % (g.number, g.white.name, g.black.name))
                    elif g.gtype == game.EXAMINED:
                        conn.write(_('(examining game %d)\n') % (g.number))
                    else:
                        assert(False)
            else:
                if u.last_logout is None:
                    conn.write(_('%s has never connected.\n') % u.name)
                else:
                    conn.write(_('Last disconnected: %s\n') % time.strftime("%a %b %e, %H:%M %Z %Y", u.last_logout.timetuple()))

            conn.write('\n')

            #if u.is_guest:
            #    conn.write(_('%s is NOT a registered player.\n') % u.name)
            if not u.is_guest:
                rating.show_ratings(u, conn)
            if u.admin_level > admin.Level.user:
                conn.write(A_('Admin level: %s\n') % admin.level.to_str(u.admin_level))
            if conn.user.admin_level > admin.Level.user:
                if not u.is_guest:
                    conn.write(A_('Email:       %s\n') % u.email)
                    conn.write(A_('Real name:   %s\n') % u.real_name)
                if u.is_online:
                    conn.write(A_('Host:        %s\n') % u.session.conn.ip)

            if u.is_online:
                if u.session.use_timeseal:
                    conn.write(_('Timeseal:    On\n'))
                elif u.session.use_zipseal:
                    conn.write(_('Zipseal:     On\n'))
                else:
                    conn.write(_('Zipseal:     Off\n'))

            notes = u.notes
            if len(notes) > 0:
                conn.write('\n')
                prev_max = 0
                for (num, txt) in sorted(notes.iteritems()):
                    num = int(num)
                    assert(num >= prev_max + 1)
                    assert(num <= 10)
                    if num > prev_max + 1:
                        # fill in blank lines
                        for j in range(prev_max + 1, num):
                            conn.write(_("%2d: %s\n") % (j, ''))
                    conn.write(_("%2d: %s\n") % (num, txt))
                    prev_max = num
                conn.write('\n')

@ics_command('flag', '', admin.Level.user)
class Flag(Command):
    def run(self, args, conn):
        if not conn.user.session.game:
            conn.write(_("You are not playing a game.\n"))
            return
        g = conn.user.session.game
        if not g.clock.check_flag(g, g.get_user_opp_side(conn.user)):
            conn.write(_('Your opponent is not out of time.\n'))

@ics_command('follow', 'w', admin.Level.user)
class Follow(Command):
    def run(self, args, conn):
        conn.write('TODO: FOLLOW\n')

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

@ics_command('history', 'o', admin.Level.user)
class History(Command):
    def run(self, args, conn):
        u = None
        if args[0] is not None:
            u = user.find.by_prefix_for_user(args[0], conn, min_len=2)
        else:
            u = conn.user
        if u:
            history.show_for_user(u, conn)

@ics_command('password', 'WW', admin.Level.user)
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

@ics_command('uptime', '', admin.Level.user)
class Uptime(Command):
    def run(self, args, conn):
        conn.write(_("Server location: %s   Server version : %s\n") % (server.location, server.version))
        conn.write(_("The server has been up since %s.\n") % time.strftime("%a %b %e, %H:%M %Z %Y", time.localtime(server.start_time)))
        conn.write(_("Up for: %s\n") % timer.hms_words(time.time() -
            server.start_time))

@ics_command('who', 'T', admin.Level.user)
class Who(Command):
    def run(self, args, conn):
        count = 0
        for u in online.itervalues():
            conn.write(u.get_display_name() + '\n')
            count = count + 1
        conn.write('\n')
        conn.write(ngettext('%d player displayed.\n\n', '%d players displayed.\n\n', count) % count)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
