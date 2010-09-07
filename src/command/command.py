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
import channel
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

@ics_command('allobservers', 'o', admin.Level.user)
class Allobservers(Command):
    def run(self, args, conn):
        if args[0] is not None:
            g = game.from_name_or_number(args[0], conn)
            if g:
                if not g.observers:
                    conn.write(_('No one is observing game %d.\n')
                        % g.number)
                else:
                    g.show_observers(conn)
        else:
            for g in game.games.itervalues():
                g.show_observers(conn)

@ics_command('cshout', 'S', admin.Level.user)
class Cshout(Command):
    @requires_registration
    def run(self, args, conn):
        if not conn.user.vars['cshout']:
            conn.write(_("(Did not c-shout because you are not listening to c-shouts)\n"))
        else:
            count = 0
            name = conn.user.name
            dname = conn.user.get_display_name()
            for u in online.itervalues():
                if u.vars['cshout']:
                    if name not in u.censor:
                        u.write(_("%s c-shouts: %s\n") %
                            (dname, args[0]))
                        count += 1
            conn.write(ngettext("(c-shouted to %d player)\n", "(c-shouted to %d players)\n", count) % count)

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

                if len(u.session.games) > 0:
                    g = u.session.games.current()
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
        if len(conn.user.session.games) == 0:
            conn.write(_("You are not playing a game.\n"))
            return
        g = conn.user.session.games.current()
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

@ics_command('inchannel', 'n', admin.Level.user)
class Inchannel(Command):
    def run(self, args, conn):
        if args[0] is not None:
            if type(args[0]) != str:
                try:
                    ch = channel.chlist.all[args[0]]
                except KeyError:
                    conn.write(_('Invalid channel number.\n'))
                else:
                    on = ch.get_online()
                    if len(on) > 0:
                        conn.write("%s: %s\n" % (ch.get_display_name(), ' '.join(on)))
                    count = len(on)
                    conn.write(ngettext('There is %d player in channel %d.\n', 'There are %d players in channel %d.\n', count) % (count, args[0]))
            else:
                conn.write("INCHANNEL USER\n")
        else:
            for ch in channel.chlist.all.values():
                on = ch.get_online()
                if len(on) > 0:
                    conn.write("%s: %s\n" % (ch.get_display_name(), ' '.join(on)))

@ics_command('iset', 'wS', admin.Level.user)
class Iset(Command):
    def run(self, args, conn):
        [name, val] = args
        try:
            v = var.ivars.get(name)
            v.set(conn.user, val)
        except trie.NeedMore as e:
            assert(len(e.matches) >= 2)
            conn.write(_('Ambiguous ivariable "%s". Matches: %s\n') % (name, ' '.join([v.name for v in e.matches])))
        except KeyError:
            conn.write(_('No such ivariable "%s".\n') % name)
        except var.BadVarError:
            conn.write(_('Bad value given for ivariable "%s".\n') % v.name)

@ics_command('it', 'S', admin.Level.user)
class It(Command):
    @requires_registration
    def run(self, args, conn):
        if not conn.user.vars['shout']:
            conn.write(_("(Did not it-shout because you are not listening to shouts)\n"))
        else:
            count = 0
            name = conn.user.name
            dname = conn.user.get_display_name()
            for u in online.itervalues():
                if u.vars['shout']:
                    if name not in u.censor:
                        u.write(_("--> %s %s\n") %
                            (dname, args[0]))
                        count += 1
            conn.write(ngettext("(it-shouted to %d player)\n", "(it-shouted to %d players)\n", count) % count)

@ics_command('ivariables', 'o', admin.Level.user)
class Ivariables(Command):
    def run(self, args, conn):
        if args[0] is None:
            u = conn.user
        else:
            u = user.find.by_prefix_for_user(args[0], conn,
                online_only=True)

        if u:
            conn.write(_("Interface variable settings of %s:\n\n") % u.name)
            for (vname, val) in u.session.ivars.iteritems():
                v = var.ivars[vname]
                if val is not None and v.display_in_vars:
                    conn.write("%s\n" % v.get_display_str(val))
            conn.write("\n")

@ics_command('match', 'wt', admin.Level.user)
class Match(Command):
    def run(self, args, conn):
        if len(conn.user.session.games) != 0:
            conn.write(_("You can't challenge while you are playing a game.\n"))
            return
        u = user.find.by_prefix_for_user(args[0], conn, online_only=True)
        if not u:
            return
        if u == conn.user:
            conn.write(_("You can't match yourself.\n"))
            return

        if conn.user.name in u.censor:
            conn.write(_("%s is censoring you.\n") % u.name)
            return
        if conn.user.name in u.noplay:
            conn.write(_("You are on %s's noplay list.\n") % u.name)
            return
        if not u.vars['open']:
            conn.write(_("%s is not open to match requests.\n") % u.name)
            return
        if len(u.session.games) != 0:
            conn.write(_("%s is playing a game.\n") % u.name)

        if not conn.user.vars['open']:
            var.vars['open'].set(conn.user, '1')
        offer.Challenge(conn.user, u, args[1])


@ics_command('observe', 'i', admin.Level.user)
class Observe(Command):
    def run(self, args, conn):
        if args[0] in ['/l', '/b', '/s', '/S', '/w', '/z', '/B', '/L', '/x']:
            conn.write('TODO: observe flag\n')
            return
        g = game.from_name_or_number(args[0], conn)
        if g:
            if g in conn.user.session.observed:
                conn.write(_('You are already observing game %d.\n' % g.number))
            elif conn.user == g.white or conn.user == g.black:
                conn.write(_('You cannot observe yourself.\n'))
            else:
                assert(conn.user not in g.observers)
                conn.user.session.observed.add(g)
                g.observe(conn.user)

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

@ics_command('rmatch', 'wwt', admin.Level.user)
class Rmatch(Command):
    def run(self, args, conn):
        if not conn.user.has_title('TD'):
            conn.write(_('Only TD programs are allowed to use this command\n'))
            return
        u1 = user.find.by_prefix_for_user(args[0], conn, online_only=True)
        if not u1:
            return
        u2 = user.find.by_prefix_for_user(args[1], conn, online_only=True)
        if not u2:
            return
        # ignore censor lists, noplay lists, and open var
        if u1 == u2:
            conn.write(_("A player cannot match himself or herself.\n"))
            return
        if len(u1.session.games) != 0:
            conn.write(_("%s is playing a game.\n") % u1.name)
            return
        if len(u2.session.games) != 0:
            conn.write(_("%s is playing a game.\n") % u2.name)
            return
        offer.Challenge(u1, u2, args[2])


@ics_command('set', 'wT', admin.Level.user)
class Set(Command):
    def run(self, args, conn):
        # val can be None if the user gave no value
        [name, val] = args
        try:
            v = var.vars.get(name)
            v.set(conn.user, val)
        except trie.NeedMore as e:
            assert(len(e.matches) >= 2)
            conn.write(_('Ambiguous variable "%s". Matches: %s\n') % (name, ' '.join([v.name for v in e.matches])))
        except KeyError:
            conn.write(_('No such variable "%s".\n') % name)
        except var.BadVarError:
            conn.write(_('Bad value given for variable "%s".\n') % v.name)

@ics_command('shout', 'S', admin.Level.user)
class Shout(Command):
    @requires_registration
    def run(self, args, conn):
        if not conn.user.vars['shout']:
            conn.write(_("(Did not shout because you are not listening to shouts)\n"))
        else:
            count = 0
            name = conn.user.name
            dname = conn.user.get_display_name()
            for u in online.itervalues():
                if u.vars['shout']:
                    if name not in u.censor:
                        u.write(_("%s shouts: %s\n") % (name, args[0]))
                        count += 1
            conn.write(ngettext("(shouted to %d player)\n", "(shouted to %d players)\n", count) % count)

@ics_command('summon', 'w', admin.Level.user)
class Summon(Command):
    def run(self, args, conn):
        u = user.find.by_prefix_for_user(args[0], conn)
        if u == conn.user:
            conn.write(_("You can't summon yourself.\n"))
        if conn.user.admin_level <= admin.level.user:
            if conn.user.name in u.censor:
                conn.write(_("%s is censoring you.\n") % u.name)
                return
            if conn.user.name not in u.notifiers:
                conn.write(_('You cannot summon a player who doesn\'t have you on his or her notify list.\n'))
                return
        # TODO: localize for the user being summoned
        u.write('\a\n%s needs to speak to you.  To contact him or her type "tell %s hello".\n' % (conn.user.name, conn.user.name))
        conn.write(_('Summoning sent to "%s".\n') % u.name)
        # TODO: add to idlenotify list

@ics_command('style', 'd', admin.Level.user)
class Style(Command):
    def run(self, args, conn):
        #conn.write('Warning: the "style" command is deprecated.  Please use "set style" instead.\n')
        var.vars['style'].set(conn.user, str(args[0]))

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

@ics_command('unobserve', 'n', admin.Level.user)
class Unobserve(Command):
    def run(self, args, conn):
        if args[0] is not None:
            g = game.from_name_or_number(args[0], conn)
            if g:
                if g in conn.user.session.observed:
                    g.unobserve(conn.user)
                else:
                    conn.write(_('You are not observing game %d.\n')
                        % g.number)
        else:
            if not conn.user.session.observed:
                conn.write(_('You are not observing any games.\n'))
            else:
                for g in conn.user.session.observed.copy():
                    g.unobserve(conn.user)
                    #conn.write(_('Removing game %d from observation list.\n') % g.number)
                    #g.observers.remove(conn.user)
                assert(not conn.user.session.observed)

@ics_command('uptime', '', admin.Level.user)
class Uptime(Command):
    def run(self, args, conn):
        conn.write(_("Server location: %s   Server version : %s\n") % (server.location, server.version))
        conn.write(_("The server has been up since %s.\n") % time.strftime("%a %b %e, %H:%M %Z %Y", time.localtime(server.start_time)))
        conn.write(_("Up for: %s\n") % timer.hms_words(time.time() -
            server.start_time))

@ics_command('variables', 'o', admin.Level.user)
class Variables(Command):
    def run(self, args, conn):
        if args[0] is None:
            u = conn.user
        else:
            u = user.find.by_prefix_for_user(args[0], conn)

        if u:
            conn.write(_("Variable settings of %s:\n\n") % u.name)
            for (vname, val) in u.vars.iteritems():
                v = var.vars[vname]
                if val is not None and v.display_in_vars:
                    conn.write("%s\n" % v.get_display_str(val))
            conn.write("\n")

@ics_command('who', 'T', admin.Level.user)
class Who(Command):
    def run(self, args, conn):
        count = 0
        for u in online.itervalues():
            conn.write(u.get_display_name() + '\n')
            count = count + 1
        conn.write('\n')
        conn.write(ngettext('%d player displayed.\n\n', '%d players displayed.\n\n', count) % count)

@ics_command('znotify', 'o', admin.Level.user)
class Znotify(Command):
    def run(self, args, conn):
        if args[0] is not None:
            if args[0] != 'n':
                raise BadCommandError()
            show_idle = True
        else:
            show_idle = False
        notifiers = [name for name in conn.user.notifiers
            if online.is_online(name)]
        if len(notifiers) == 0:
            conn.write(_('No one from your notify list is logged on.\n'))
        else:
            conn.write(_('Present company on your notify list:\n   %s\n') %
                ' '.join(notifiers))

        name = conn.user.name
        notified = [u.name for u in online if name in u.notifiers]
        if len(notified) == 0:
            conn.write(_('No one logged in has you on their notify list.\n'))
        else:
            conn.write(_('The following players have you on their notify list:\n   %s\n') %
                ' '.join(notified))

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
