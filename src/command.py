import time
import datetime
import re

import user
import trie
import admin
import var
import list
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
from db import db

class QuitException(Exception):
    pass

class Command(object):
    def __init__(self, name, param_str, run, admin_level):
        self.name = name
        self.param_str = param_str
        self.run = run
        self.admin_level = admin_level

    def help(self, conn):
        conn.write("help for %s\n" % self.name)

    def usage(self, conn):
        conn.write("Usage: TODO for %s\n" % self.name)

class CommandList(object):
    def __init__(self):
        # the trie data structure allows for efficiently finding
        # a command given a substring
        self.cmds = trie.Trie()
        self.admin_cmds = trie.Trie()
        self._add(Command('abort', 'n', self.abort, admin.Level.user))
        self._add(Command('accept', 'n', self.accept, admin.Level.user))
        self._add(Command('aclearhistory', 'w', self.aclearhistory, admin.Level.admin))
        self._add(Command('addlist', 'ww', self.addlist, admin.Level.user))
        self._add(Command('addplayer', 'WWS', self.addplayer, admin.Level.admin))
        self._add(Command('alias', 'oT', self.alias, admin.Level.user))
        self._add(Command('allobservers', 'o', self.allobservers, admin.Level.user))
        self._add(Command('announce', 'S', self.announce, admin.Level.admin))
        self._add(Command('annunreg', 'S', self.annunreg, admin.Level.admin))
        self._add(Command('areload', '', self.areload, admin.Level.god))
        self._add(Command('asetadmin', 'wd', self.asetadmin, admin.Level.admin))
        self._add(Command('asetpasswd', 'wW', self.asetpasswd, admin.Level.admin))
        self._add(Command('asetrating', 'wwwddfddd', self.asetrating, admin.Level.admin))
        self._add(Command('cnewsd', 'd', self.cnewse, admin.Level.admin))
        self._add(Command('cnewse', 'dp', self.cnewse, admin.Level.admin))
        self._add(Command('cnewsf', 'dT', self.cnewsf, admin.Level.admin))
        self._add(Command('cnewsi', 'S', self.cnewsi, admin.Level.admin))
        self._add(Command('cnewsp', 'd', self.cnewsp, admin.Level.admin))
        self._add(Command('cnewst', 'dS', self.cnewst, admin.Level.admin))
        self._add(Command('cshout', 'S', self.cshout, admin.Level.user))
        self._add(Command('date', '', self.date, admin.Level.user))
        self._add(Command('decline', 'n', self.decline, admin.Level.user))
        self._add(Command('draw', 'o', self.draw, admin.Level.user))
        self._add(Command('eco', 'oo', self.eco, admin.Level.user))
        self._add(Command('examine', 'on', self.examine, admin.Level.user))
        self._add(Command('finger', 'ooo', self.finger, admin.Level.user))
        self._add(Command('flag', '', self.flag, admin.Level.user))
        self._add(Command('follow', 'w', self.follow, admin.Level.user))
        self._add(Command('forward', 'p', self.forward, admin.Level.user))
        self._add(Command('help', 'o', self.help, admin.Level.user))
        self._add(Command('history', 'o', self.history, admin.Level.user))
        self._add(Command('inchannel', 'n', self.inchannel, admin.Level.user))
        self._add(Command('iset', 'wS', self.iset, admin.Level.user))
        self._add(Command('it', 'S', self.it, admin.Level.user))
        self._add(Command('ivariables', 'o', self.ivariables, admin.Level.user))
        self._add(Command('match', 'wt', self.match, admin.Level.user))
        self._add(Command('moves', 'n', self.moves, admin.Level.user))
        self._add(Command('news', 'p', self.news, admin.Level.user))
        self._add(Command('nuke', 'w', self.nuke, admin.Level.admin))
        self._add(Command('observe', 'i', self.observe, admin.Level.user))
        self._add(Command('password', 'WW', self.password, admin.Level.user))
        self._add(Command('qtell', 'iS', self.qtell, admin.Level.user))
        self._add(Command('quit', '', self.quit, admin.Level.user))
        self._add(Command('refresh', 'n', self.refresh, admin.Level.user))
        self._add(Command('remplayer', 'w', self.remplayer, admin.Level.admin))
        self._add(Command('resign', 'o', self.resign, admin.Level.user))
        self._add(Command('rmatch', 'wwt', self.rmatch, admin.Level.user))
        self._add(Command('set', 'wT', self.set, admin.Level.user))
        self._add(Command('shout', 'S', self.shout, admin.Level.user))
        self._add(Command('showlist', 'o', self.showlist, admin.Level.user))
        self._add(Command('sublist', 'ww', self.sublist, admin.Level.user))
        self._add(Command('summon', 'w', self.summon, admin.Level.user))
        self._add(Command('style', 'd', self.style, admin.Level.user))
        self._add(Command('tell', 'nS', self.tell, admin.Level.user))
        self._add(Command('unalias', 'w', self.unalias, admin.Level.user))
        self._add(Command('unobserve', 'n', self.unobserve, admin.Level.user))
        self._add(Command('uptime', '', self.uptime, admin.Level.user))
        self._add(Command('variables', 'o', self.variables, admin.Level.user))
        self._add(Command('who', 'T', self.who, admin.Level.user))
        self._add(Command('withdraw', 'n', self.withdraw, admin.Level.user))
        self._add(Command('xtell', 'nS', self.xtell, admin.Level.user))
        self._add(Command('znotify', 'o', self.znotify, admin.Level.user))

    def _add(self, cmd):
        self.admin_cmds[cmd.name] = cmd
        if cmd.admin_level <= admin.Level.user:
            self.cmds[cmd.name] = cmd

    def abort(self, args, conn):
        if not conn.user.session.games:
            conn.write(_("You are not playing a game.\n"))
            return
        if len(conn.user.session.games) > 1:
            conn.write(_('Please use "simabort" for simuls.\n'))
            return
        g = conn.user.session.games.primary()
        if g.variant.pos.ply < 2:
            g.abort('Game aborted on move 1 by %s' % conn.user.name)
        else:
            offer.Abort(g, conn.user)

    def accept(self, args, conn):
        if not conn.user.session.offers_received:
            conn.write(_('You have no pending offers from other players.\n'))
            return
        if args[0] is None:
            if len(conn.user.session.offers_received) > 1:
                conn.write(_('You have more than one pending offer. Use "pending" to see them and "accept n" to choose one.\n'))
                return
            conn.user.session.offers_received[0].accept()
        else:
            conn.write('TODO: ACCEPT PARAM\n')

    def aclearhistory(self, args, conn):
        name = args[0]
        u = user.find.by_name_exact_for_user(name, conn)
        if u:
            # disallow clearing history for higher adminlevels?
            u.clear_history()
            u.write(A_('\nHistory of %s cleared.\n') % conn.user.name)

    def addlist(self, args, conn):
        try:
            ls = list.lists.get(args[0])
        except KeyError:
            conn.write(_('''\"%s\" does not match any list name.\n''' % args[0]))
        except trie.NeedMore as e:
            conn.write(_('''Ambiguous list \"%s\". Matches: %s\n''') % (args[0], ' '.join([r.name for r in e.matches])))
        else:
            try:
                ls.add(args[1], conn)
            except list.ListError as e:
                conn.write(e.reason)

    def addplayer(self, args, conn):
        [name, email, real_name] = args
        try:
            u = user.find.by_name_exact(name)
        except user.UsernameException as e:
            conn.write(e.reason + '\n')
        else:
            if u:
                conn.write('A player named %s is already registered.\n' % name)
            else:
                passwd = user.create.passwd()
                user.create.new(name, email, passwd, real_name)
                conn.write(A_('Added: >%s< >%s< >%s< >%s<\n') % (name, real_name, email, passwd))

    def alias(self, args, conn):
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

    def allobservers(self, args, conn):
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

    def announce(self, args, conn):
        count = 0
        # the announcement message isn't localized
        for u in online.itervalues():
            if u != conn.user:
                count = count + 1
                u.write("\n\n    **ANNOUNCEMENT** from %s: %s\n\n" % (conn.user.name, args[0]))
        conn.write("(%d) **ANNOUNCEMENT** from %s: %s\n\n" % (count, conn.user.name, args[0]))

    def annunreg(self, args, conn):
        count = 0
        # the announcement message isn't localized
        for u in online.itervalues():
            if u != conn.user and u.is_guest:
                count = count + 1
                u.write("\n\n    **UNREG ANNOUNCEMENT** from %s: %s\n\n" % (conn.user.name, args[0]))
        conn.write("(%d) **UNREG ANNOUNCEMENT** from %s: %s\n\n" % (count, conn.user.name, args[0]))

    def areload(self, args, conn):
        reload.reload_all(conn)

    def asetadmin(self, args, conn):
        [name, level] = args
        u = user.find.by_name_exact_for_user(name, conn)
        if u:
            # Note: it's possible to set the admin level
            # of a guest.
            if not admin.checker.check_user_operation(conn.user, u):
                conn.write('You can only set the adminlevel for players below your adminlevel.\n')
            elif not admin.checker.check_level(conn.user.admin_level, level):
                conn.write('''You can't promote someone to or above your adminlevel.\n''')
            else:
                u.set_admin_level(level)
                conn.write('''Admin level of %s set to %d.\n''' % (name, level))
                if u.is_online:
                    u.write('''\n\n%s has set your admin level to %d.\n\n''' % (conn.user.name, level))

    def asetpasswd(self, args, conn):
        (name, passwd) = args
        u = user.find.by_name_exact_for_user(name, conn)
        if u:
            if u.is_guest:
                conn.write('You cannot set the password of an unregistered player!\n')
            elif not admin.checker.check_user_operation(conn.user, u):
                conn.write('You can only set the password of players below your adminlevel.\n')
            elif not user.is_legal_passwd(passwd):
                conn.write('"%s" is not a valid password.\n' % passwd)
            else:
                u.set_passwd(passwd)
                conn.write('Password of %s changed to %s.\n' % (name, '*' * len(passwd)))
                if u.is_online:
                    u.write(_('\n%s has changed your password.\n') % conn.user.name)

    def asetrating(self, args, conn):
        (name, speed_name, variant_name, urating, rd, volatility, win,
            loss, draw) = args
        u = user.find.by_prefix_for_user(name, conn)
        if not u:
            return
        if u.is_guest:
            conn.write(A_('You cannot set the rating of an unregistered player.\n'))
            return
        try:
            sv = speed_variant.from_names(speed_name, variant_name)
        except KeyError:
            conn.write(A_('Unknown speed and variant "%s %s".\n') %
                speed_name, variant_name)
            return
        if urating == 0:
            u.del_rating(sv)
            conn.write(A_('Cleared %s %s rating for %s.\n' %
                (speed_name, variant_name, name)))
        else:
            u.set_rating(sv, urating, rd, volatility, win, loss, draw,
                datetime.datetime.utcnow())
            conn.write(A_('Set %s %s rating for %s.\n' %
                (speed_name, variant_name, name)))
        # notify the user?

    def cnewsd(self, args, conn):
        pass
    def cnewse(self, args, conn):
        pass
    def cnewsf(self, args, conn):
        pass
    def cnewsi(self, args, conn):
        if len(args[0]) > 45:
            conn.write(A_('The news title exceeds the 45-character maximum length; not posted.\n'))
            return
        db.add_news(args[0], conn.user, is_admin=False)
    def cnewsp(self, args, conn):
        pass
    def cnewst(self, args, conn):
        pass

    def cshout(self, args, conn):
        if conn.user.is_guest:
            conn.write(_("Only registered players can use the cshout command.\n"))
        elif not conn.user.vars['cshout']:
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

    def date(self, args, conn):
        t = time.time()
        #conn.write(_("Local time     - %s\n") % )
        conn.write(_("Server time    - %s\n") % time.strftime("%a %b %e, %H:%M %Z %Y", time.localtime(t)))
        conn.write(_("GMT            - %s\n") % time.strftime("%a %b %e, %H:%M GMT %Y", time.gmtime(t)))

    def decline(self, args, conn):
        if len(conn.user.session.offers_received) == 0:
            conn.write(_('You have no pending offers from other players.\n'))
            return
        if args[0] is None:
            if len(conn.user.session.offers_received) > 1 and args[0] is None:
                conn.write(_('You have more than one pending offer. Use "pending" to see them and "decline n" to choose one.\n'))
                return
            conn.user.session.offers_received[0].decline()
        else:
            conn.write('TODO: DECLINE PARAM\n')

    def draw(self, args, conn):
        if args[0] is None:
            if len(conn.user.session.games) == 0:
                conn.write(_("You are not playing a game.\n"))
                return
            g = conn.user.session.games.primary()
            offer.Draw(g, conn.user)
        else:
            conn.write('TODO: DRAW PARAM\n')

    eco_pat = re.compile(r'[a-z][0-9][0-9][a-z]?')
    nic_pat = re.compile(r'[a-z][a-z]\.[0-9][0-9]')
    def eco(self, args, conn):
        g = None
        if args[1] is not None:
            assert(args[0] is not None)
            rows = []
            if args[0] == 'e':
                if not self.eco_pat.match(args[1]):
                    conn.write(_("You haven't specified a valid ECO code.\n"))
                else:
                    rows = db.look_up_eco(args[1])
            elif args[0] == 'n':
                if not self.nic_pat.match(args[1]):
                    conn.write(_("You haven't specified a valid NIC code.\n"))
                else:
                    rows = db.look_up_nic(args[1])
            else:
                raise BadCommandError()
            for row in rows:
                if row['eco'] is None:
                    row['eco'] = 'A00'
                if row['nic'] is None:
                    row['nic'] = '-----'
                if row['long_'] is None:
                    row['long_'] = 'Unknown / not matched'
                assert(row['fen'] is not None)
                conn.write('\n')
                conn.write('  ECO: %s\n' % row['eco'])
                conn.write('  NIC: %s\n' % row['nic'])
                conn.write(' LONG: %s\n' % row['long_'])
                conn.write('  FEN: %s\n' % row['fen'])
        elif args[0] is not None:
            g = game.from_name_or_number(args[0], conn)
        else:
            if not conn.user.session.games:
                conn.write(_("You are not playing, examining, or observing a game.\n"))
            else:
                g = conn.user.session.games.primary()

        if g is not None:
            (ply, eco, long) = g.get_eco()
            (nicply, nic) = g.get_nic()
            conn.write(_('Eco for game %d (%s vs. %s):\n') % (g.number, g.white.name, g.black.name))
            conn.write(_(' ECO[%3d]: %s\n') % (ply, eco))
            conn.write(_(' NIC[%3d]: %s\n') % (nicply, nic))
            conn.write(_('LONG[%3d]: %s\n') % (ply, long))

    def examine(self, args, conn):
        if len(conn.user.session.games) != 0:
            if conn.user.session.games.values()[0].gtype == game.EXAMINE:
                conn.write(_("You are already examining a game.\n"))
            else:
                conn.write(_("You are playing a game.\n"))
            return
        if args[1] == 'b':
            conn.write('TODO: EXAMINE BOARD\n')
            return
        conn.write(_("Starting a game in examine (scratch) mode.\n"))
        game.ExaminedGame(conn.user)

    def finger(self, args, conn):
        u = None
        if args[0] is not None:
            u = user.find.by_prefix_for_user(args[0], conn, min_len=2)
        else:
            u = conn.user
        if u:
            conn.write(_('Finger of %s:\n\n') % u.get_display_name())

            if u.is_online:
                conn.write(_('On for: %s   Idle: %s\n') % (u.session.get_online_time(), u.session.get_idle_time()))

                if len(u.session.games) > 0:
                    g = u.session.games.primary()
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

    def flag(self, args, conn):
        if len(conn.user.session.games) == 0:
            conn.write(_("You are not playing a game.\n"))
            return
        g = conn.user.session.games.primary()
        if not g.clock.check_flag(g, g.get_user_opp_side(conn.user)):
            conn.write(_('Your opponent is not out of time.\n'))

    def follow(self, args, conn):
        conn.write('TODO: FOLLOW\n')

    def forward(self, args, conn):
        n = args[0] if args[0] is not None else 1
        if not conn.user.session.games or conn.user.session.games.primary().gtype != game.EXAMINED:
            conn.write(_("You are not examining a game.\n"))
            return
        conn.write('TODO: forward %d\n' % n)

    def help(self, args, conn):
        if conn.user.admin_level > admin.level.user:
            cmds = [c.name for c in command_list.admin_cmds.itervalues()]
        else:
            cmds = [c.name for c in command_list.cmds.itervalues()]
        conn.write('This server is under development.\n\nRecognized commands: %s\n' % ' '.join(cmds))

    def history(self, args, conn):
        u = None
        if args[0] is not None:
            u = user.find.by_prefix_for_user(args[0], conn, min_len=2)
        else:
            u = conn.user
        if u:
            history.show_for_user(u, conn)

    def inchannel(self, args, conn):
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

    def iset(self, args, conn):
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

    def it(self, args, conn):
        if conn.user.is_guest:
            conn.write(_("Only registered players can use the it command.\n"))
        elif not conn.user.vars['shout']:
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

    def ivariables(self, args, conn):
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

    def match(self, args, conn):
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

    def rmatch(self, args, conn):
        if 'TD' not in conn.user.get_titles():
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

    def moves(self, args, conn):
        # similar to "refresh"
        g = None
        if args[0] is not None:
            g = game.from_name_or_number(args[0], conn)
        else:
            if len(conn.user.session.games) > 0:
                g = conn.user.session.games.primary()
            else:
                conn.write(_("You are not playing, examining, or observing a game.\n"))
        if g is not None:
            g.write_moves(conn)

    def news(self, args, conn):
        if args[0] is not None:
            conn.write('TODO: news #\n')
        else:
            news = db.get_recent_news(is_admin=False)
            if len(news) == 0:
                conn.write(_('There is no news.\n'))
            for item in reversed(news):
                conn.write('%4d (%s) %s\n' % (item['news_id'], item['news_date'], item['news_title']))

    def nuke(self, args, conn):
        u = user.find.by_name_exact_for_user(args[0], conn)
        if u:
            if not admin.checker.check_user_operation(conn.user, u):
                conn.write("You need a higher adminlevel to nuke %s!\n" % u.name)
            elif not u.is_online:
                conn.write("%s is not logged in.\n"  % u.name)
            else:
                u.write('\n\n**** You have been kicked out by %s! ****\n\n' % conn.user.name)
                u.session.conn.loseConnection('nuked')
                conn.write('Nuked: %s\n' % u.name)

    def observe(self, args, conn):
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

    def password(self, args, conn):
        if conn.user.is_guest:
            conn.write(_("Setting a password is only for registered players.\n"))
        else:
            [oldpass, newpass] = args
            if not conn.user.check_passwd(oldpass):
                conn.write(_("Incorrect password; password not changed!\n"))
            else:
                conn.user.set_passwd(newpass)
                conn.write(_("Password changed to %s.\n") % ('*' * len(newpass)))

    def quit(self, args, conn):
        raise QuitException()

    def qtell(self, args, conn):
        if 'TD' not in conn.user.get_titles():
            conn.write(_('Only TD programs are allowed to use this command\n'))
            return
        msg = args[1].replace('\\n', '\n:').replace('\\b', '\x07').replace('\\H', '\x1b[7m').replace('\\h', '\x1b[0m')
        msg = '\n:%s\n' % msg
        ret = 0 # 0 means success
        if type(args[0]) == type(1):
            # qtell channel
            try:
                ch = channel.chlist[args[0]]
            except KeyError:
                ret = 1
            else:
                ch.qtell(msg)
        else:
            # qtell user
            try:
                u = user.find.by_name_exact(args[0])
                if not u or not u.is_online:
                    ret = 1
                else:
                    args[0] = u.name
                    u.write(msg)
            except user.UsernameException:
                ret = 1
        conn.write('*qtell %s %d*\n' % (args[0], ret))

    def remplayer(self, args, conn):
        name = args[0]
        u = user.find.by_name_exact_for_user(name, conn)
        if u:
            if not admin.checker.check_user_operation(conn.user, u):
                conn.write('''You can't remove an admin with a level higher than or equal to yourself.\n''')
            elif u.is_online:
                conn.write("%s is logged in.\n" % u.name)
            else:
                u.remove()
                conn.write("Player %s removed.\n" % name)

    def refresh(self, args, conn):
        g = None
        if args[0] is not None:
            g = game.from_name_or_number(args[0], conn)
        else:
            if len(conn.user.session.games) > 0:
                g = conn.user.session.games.primary()
            else:
                conn.write(_("You are not playing, examining, or observing a game.\n"))
        if g is not None:
            conn.user.send_board(g)

    def resign(self, args, conn):
        if args[0] is not None:
            conn.write('TODO: RESIGN PLAYER\n')
            return
        if len(conn.user.session.games) == 0:
            conn.write(_("You are not playing a game.\n"))
            return
        g = conn.user.session.games.primary()
        g.resign(conn.user)

    def set(self, args, conn):
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

    def shout(self, args, conn):
        if conn.user.is_guest:
            conn.write(_("Only registered players can use the shout command.\n"))
        elif not conn.user.vars['shout']:
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

    def showlist(self, args, conn):
        if args[0] is None:
            for c in list.lists.itervalues():
                conn.write('%s\n' % c.name)
            return

        try:
            ls = list.lists.get(args[0])
        except KeyError:
            conn.write(_('''\"%s\" does not match any list name.\n''' % args[0]))
        except trie.NeedMore as e:
            conn.write(_('''Ambiguous list \"%s\". Matches: %s\n''') % (args[0], ' '.join([r.name for r in e.matches])))
        else:
            try:
                ls.show(conn)
            except list.ListError as e:
                conn.write(e.reason)

    def sublist(self, args, conn):
        try:
            ls = list.lists.get(args[0])
        except KeyError:
            conn.write(_('''\"%s\" does not match any list name.\n''' % args[0]))
        except trie.NeedMore as e:
            conn.write(_('''Ambiguous list \"%s\". Matches: %s\n''') % (args[0], ' '.join([r.name for r in e.matches])))
        else:
            try:
                ls.sub(args[1], conn)
            except list.ListError as e:
                conn.write(e.reason)

    def summon(self, args, conn):
        u = user.find.by_prefix_for_user(args[0], conn)
        if u == conn.user:
            conn.write(_("You can't summon yourself.\n"))
        if conn.user.admin_level <= admin.level.user:
            if conn.user.name in u.censor:
                conn.write(_("%s is censoring you.\n") % u.name)
                return
            if conn.user.name not in u.notifiers:
                conn.write(_('You cannot summon a player who doesn\'t have you on his/her notify list.\n'))
                return
        # TODO: localize for the user being summoned
        u.write('\a\n%s needs to speak to you.  To contact him/her type "tell %s hello".\n' % (conn.user.name, conn.user.name))
        conn.write(_('Summoning sent to "%s".\n') % u.name)
        # TODO: add to idlenotify list

    def style(self, args, conn):
        #conn.write('Warning: the "style" command is deprecated.  Please use "set style" instead.\n')
        var.vars['style'].set(conn.user, str(args[0]))

    def tell(self, args, conn):
        (u, ch) = self._do_tell(args, conn)
        if u is not None:
            conn.session.last_tell_user = u
        else:
            conn.session.last_tell_ch = ch

    def unalias(self, args, conn):
        aname = args[0]
        if not 1 <= len(aname) < 16:
            conn.write(_("Alias names may not be more than 15 characters long.\n"))
            return

        if aname not in conn.user.aliases:
            conn.write(_('You have no alias "%s".\n') % aname)
        else:
            conn.user.set_alias(aname, None)
            conn.write(_('Alias "%s" unset.\n') % aname)

    def unobserve(self, args, conn):
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

    def uptime(self, args, conn):
        conn.write(_("Server location: %s   Server version : %s\n") % (server.location, server.version))
        conn.write(_("The server has been up since %s.\n") % time.strftime("%a %b %e, %H:%M %Z %Y", time.localtime(server.start_time)))
        conn.write(_("Up for: %s\n") % timer.hms_words(time.time() -
            server.start_time))

    def variables(self, args, conn):
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

    def xtell(self, args, conn):
        self._do_tell(args, conn)

    def _do_tell(self, args, conn):
        u = None
        ch = None
        if args[0] == '.':
            u = conn.session.last_tell_user
            if not u:
                conn.write(_("No previous tell.\n"))
            elif not u.is_online:
                # try to find the user if he or she has logged off
                # and since reconnected
                name = u.name
                u = online.find_exact(name)
                if not u:
                    conn.write(_('%s is no longer online.\n') % name)
        elif args[0] == ',':
            ch = conn.session.last_tell_ch
            if not ch:
                conn.write(_('No previous channel.\n'))
        else:
            if type(args[0]) != str:
                try:
                    ch = channel.chlist[args[0]]
                except KeyError:
                    conn.write(_('Invalid channel number.\n'))
                else:
                    if conn.user not in ch.online and (
                            'TD' not in conn.user.get_titles()):
                        conn.user.write(_('''(Not sent because you are not in channel %s.)\n''') % ch.id)
                        ch = None
            else:
                u = user.find.by_prefix_for_user(args[0], conn, online_only=True)

        if ch:
            count = ch.tell(args[1], conn.user)
            conn.write(ngettext('(told %d player in channel %d)\n', '(told %d players in channel %d)\n', count) % (count, ch.id))
        elif u:
            if conn.user.name in u.censor and conn.user.admin_level <= \
                    admin.level.user:
                conn.write(_("%s is censoring you.\n") % u.name)
            else:
                u.write('\n' + _("%s tells you: ") % conn.user.get_display_name() + args[1] + '\n')
                conn.write(_("(told %s)") % u.name + '\n')

        return (u, ch)

    def who(self, args, conn):
        count = 0
        for u in online.itervalues():
            conn.write(u.get_display_name() + '\n')
            count = count + 1
        conn.write('\n')
        conn.write(ngettext('%d player displayed.\n\n', '%d players displayed.\n\n', count) % count)

    def withdraw(self, args, conn):
        if len(conn.user.session.offers_sent) == 0:
            conn.write(_('You have no pending offers to other players.\n'))
            return
        if args[0] is None:
            if len(conn.user.session.offers_sent) > 1:
                conn.write(_('You have more than one pending offer. Use "pending" to see them and "withdraw n" to choose one.\n'))
                return
            conn.user.session.offers_sent[0].withdraw()
        else:
            conn.write('TODO: WITHDRAW PARAM\n')

    def znotify(self, args, conn):
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

command_list = CommandList()

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
