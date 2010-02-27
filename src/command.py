import re
import time
import socket
import gettext

import user
import trie
import admin
import session
import var
import list
import channel
import alias
from timer import timer
from online import online
from reload import reload
from server import server
from utf8 import checker

class InternalException(Exception):
        pass
class QuitException(Exception):
        pass
class BadCommandError(Exception):
        pass

class Command(object):
        def __init__(self, name, param_str, run, admin_level):
                self.name = name
                self.param_str = param_str
                self.run = run
                self.admin_level = admin_level

        def parse_params(self, s):
                params = []
                for c in self.param_str:
                        if c in ['d', 'i', 'w', 'W']:
                                # required argument
                                if s == None:
                                        raise BadCommandError()
                                else:
                                        m = re.split(r'\s+', s, 1)
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
                                        s = m[1] if len(m) > 1 else None
                        elif c in ['o', 'n', 'p']:
                                # optional argument
                                if s == None:
                                        param = None
                                else:
                                        m = re.split(r'\s+', s, 1)
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
                                if s == None or len(s) == 0:
                                        raise BadCommandError()
                                param = s
                                s = None
                        elif c == 'T':
                                # optional string to end
                                if s == None or len(s) == 0:
                                        param = None
                                else:
                                        param = s
                                s = None
                        else:
                                raise InternalException()
                        params.append(param)

                if not (s == None or re.match(r'^\s*$', s)):
                        # extraneous data at the end
                        raise BadCommandError()
                                
                return params

        def help(self, conn):
                conn.write("help for %s\n" % self.name)

class CommandList(object):
        def __init__(self):
                # the trie data structure allows for efficiently finding
                # a command given a substring
                self.cmds = trie.Trie()
                self.admin_cmds = trie.Trie()
                self._add(Command('addlist', 'ww', self.addlist, admin.Level.user))
                self._add(Command('addplayer', 'WWS', self.addplayer, admin.Level.admin))
                self._add(Command('announce', 'S', self.announce, admin.Level.admin))
                self._add(Command('areload', '', self.areload, admin.Level.god))
                self._add(Command('asetadmin', 'wd', self.asetadmin, admin.Level.admin))
                self._add(Command('asetpasswd', 'wW', self.asetpasswd, admin.Level.admin))
                self._add(Command('date', '', self.date, admin.Level.user))
                self._add(Command('finger', 'ooo', self.finger, admin.Level.user))
                self._add(Command('follow', 'w', self.follow, admin.Level.user))
                self._add(Command('help', 'o', self.help, admin.Level.user))
                self._add(Command('inchannel', 'n', self.inchannel, admin.Level.user))
                self._add(Command('nuke', 'w', self.nuke, admin.Level.admin))
                self._add(Command('password', 'WW', self.password, admin.Level.user))
                self._add(Command('qtell', 'iS', self.qtell, admin.Level.user))
                self._add(Command('quit', '', self.quit, admin.Level.user))
                self._add(Command('remplayer', 'w', self.remplayer, admin.Level.admin))
                self._add(Command('set', 'wT', self.set, admin.Level.user))
                self._add(Command('shout', 'S', self.shout, admin.Level.user))
                self._add(Command('showlist', 'o', self.showlist, admin.Level.user))
                self._add(Command('sublist', 'ww', self.sublist, admin.Level.user))
                self._add(Command('tell', 'nS', self.tell, admin.Level.user))
                self._add(Command('uptime', '', self.uptime, admin.Level.user))
                self._add(Command('variables', 'o', self.variables, admin.Level.user))
                self._add(Command('who', 'T', self.who, admin.Level.user))
                self._add(Command('xtell', 'nS', self.xtell, admin.Level.user))

        def _add(self, cmd):
                self.admin_cmds[cmd.name] = cmd
                if cmd.admin_level <= admin.Level.user:
                        self.cmds[cmd.name] = cmd
        
        def addlist(self, args, conn):
                try:
                        list.lists.get(args[0]).add(args, conn.user)
                except KeyError:
                        conn.write(_('''\"%s\" does not match any list name.\n''' % args[0]))
                except trie.NeedMore as e:
                        conn.write(_('''Ambiguous list \"%s\". Matches: %s\n''') % (args[0], ' '.join([r.name for r in e.matches])))
                except list.ListError as e:
                        conn.write('%s\n' % e.reason)

        def addplayer(self, args, conn):
                [name, email, real_name] = args
                try:
                        u = user.find.by_name_exact(name)
                except user.UsernameException as e:
                        conn.write(e.reason + '\n')
                else:
                        if u:
                                conn.write(_('A player named %s is already registered.\n') % name)
                        else:
                                passwd = user.create.passwd()
                                user.create.new(name, email, passwd, real_name)
                                conn.write(_('Added: >%s< >%s< >%s< >%s<\n') % (name, real_name, email, passwd))
        
        def announce(self, args, conn):
                count = 0
                for u in online.itervalues():
                        if u != conn.user:
                                count = count + 1
                                u.write_prompt(_("\n\n    **ANNOUNCEMENT** from %s: %s\n\n") % (conn.user.name, args[0]))
                conn.write(_("(%d) **ANNOUNCEMENT** from %s: %s\n\n") % (count, conn.user.name, args[0]))

        def areload(self, args, conn):
                reload.reload_all(conn)

        def asetadmin(self, args, conn):
                [name, level] = args
                u = user.find.by_name_exact_for_user(name, conn)
                if u:
                        # Note: it's possible to set the admin level
                        # of a guest.
                        if not admin.checker.check_user_operation(conn.user, u):
                                conn.write(_('You can only set the adminlevel for players below your adminlevel.'))
                        elif not admin.checker.check_level(conn.user.admin_level, level):
                                conn.write(_('''You can't promote someone to or above your adminlevel.\n'''))
                        else:
                                u.set_admin_level(level)
                                conn.write(_('''Admin level of %s set to %d.\n''' % (name, level)))
                                if u.is_online:
                                        u.write_prompt(_('''\n\n%s has set your admin level to %d.\n\n''') % (conn.user.name, level))

        def asetpasswd(self, args, conn):
                [name, passwd] = args
                u = user.find.by_name_exact_for_user(name, conn)
                if u:
                        if u.is_guest:
                                conn.write(_('You cannot set the password of an unregistered player!\n'))
                        elif not admin.checker.check_user_operation(conn.user, u):
                                conn.write(_('You can only set the password of players below your admin level.')) 
                        elif not user.is_legal_passwd(passwd):
                                conn.write(_('"%s" is not a valid password.\n') % passwd)
                        else:
                                u.set_passwd(passwd)
                                conn.write(_('Password of %s changed to %s.\n') % (name, '*' * len(passwd)))
                                if u.is_online:
                                        u.write_prompt(_('\n%s has changed your password.\n') % conn.user.name)
        
        def date(self, args, conn):
                t = time.time()
                #conn.write(_("Local time     - %s\n") % )
                conn.write(_("Server time    - %s\n") % time.strftime("%a %b %e, %H:%M %Z %Y", time.localtime(t)))
                conn.write(_("GMT            - %s\n") % time.strftime("%a %b %e, %H:%M GMT %Y", time.gmtime(t)))

        def finger(self, args, conn):
                u = None
                if args[0] != None:
                        u = user.find.by_name_or_prefix_for_user(args[0], conn, min_len=2)
                else:
                        u = conn.user
                if u:
                        conn.write(_('Finger of %s:\n\n') % u.get_display_name())
                        
                        if u.is_online:
                                conn.write(_('On for: %s   Idle: %s\n\n') % (u.session.get_online_time(), u.session.get_idle_time()))

                                if u.session.use_timeseal:
                                        conn.write(_('Timeseal: On\n\n'))
                                elif u.session.use_zipseal:
                                        conn.write(_('Zipseal: On\n\n'))
                                else:
                                        conn.write(_('Zipseal: Off\n\n'))
                                
                        else:
                                if u.last_logout == None:
                                        conn.write(_('%s has never connected.\n\n') % u.name)
                                else:
                                        #conn.write(_('Last disconnected: %s\n\n') % u.last_logout)
                                        conn.write(_('Last disconnected: %s\n\n') % time.strftime("%a %b %e, %H:%M %Z %Y", u.last_logout.timetuple()))
                        if u.is_guest:
                                conn.write(_('%s is NOT a registered player.\n') % u.name)
                        if u.admin_level > admin.Level.user:
                                conn.write(_('Admin Level: %s\n') % admin.level.to_str(u.admin_level))
        
        def follow(self, args, conn):
                conn.write('FOLLOW\n')

        def help(self, args, conn):
                if conn.user.admin_level > admin.level.user:
                        cmds = [c.name for c in command_list.admin_cmds.itervalues()]
                else:
                        cmds = [c.name for c in command_list.cmds.itervalues()]
                conn.write('This server is under development.  Recognized commands: %s\n' % ' '.join(cmds))
        
        def inchannel(self, args, conn):
                if args[0] != None:
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
                                        conn.write(gettext.ngettext('There is %d player in channel %d.\n', 'There are %d players in channel %d.\n', count) % (count, args[0]))
                        else:
                                conn.write("INCHANNEL USER\n")
                else:
                        for ch in channel.chlist.all.values():
                                on = ch.get_online()
                                if len(on) > 0:
                                        conn.write("%s: %s\n" % (ch.get_display_name(), ' '.join(on)))
        
        def nuke(self, args, conn):
                u = user.find.by_name_exact_for_user(args[0], conn)
                if u:
                        if not admin.checker.check_user_operation(conn.user, u):
		                conn.write(_("You need a higher adminlevel to nuke %s!\n") % u.name)
                        elif not u.is_online:
                                conn.write(_("%s is not logged in.\n" ) % u.name)
                        else:
                                u.write(_('\n\n**** You have been kicked out by %s! ****\n\n') % conn.user.name)
                                u.session.conn.loseConnection('nuked')
                                conn.write(_('Nuked: %s\n') % u.name)
                
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
                # 0 means success
                # XXX check for td
                if type(args[0]) == type(1):
                        # qtell channel
                        conn.write('NOT IMPLEMENTED\n')
                        conn.write('*qtell %d 1*\n' % args[0])
                else:
                        # qtell user
                        try:
                                u = user.find.by_name_exact(args[0])
                                if not u or not u.is_online:
                                        ret = 1
                                else:
                                        args[0] = u.name
                                        msg = args[1].replace('\\n', '\n:').replace('\\b', '\x07').replace('\\H', '\x1b[7m').replace('\\h', '\x1b[0m')
                                        u.write('\n:%s\n' % msg)
                                        ret = 0
                        except user.UsernameException:
                                ret = 1
                        conn.write('*qtell %s %d*\n' % (args[0], ret))
        
        def remplayer(self, args, conn):
                name = args[0]
                u = user.find.by_name_exact_for_user(name, conn)
                if u:
                        if not admin.checker.check_user_operation(conn.user, u):
                                conn.write(_('''You can't remove an admin with a level higher than or equal to yourself.\n'''))
                        elif u.is_online:
                                conn.write(_("%s is logged in.\n") % u.name)
                        else:
                                u.remove()
                                conn.write(_("Player %s removed.\n") % name)

        def set(self, args, conn):
                # val can be None if the user gave no value
                [name, val] = args
                try:
                        v = var.vars.get(name)
                        msg = v.set(conn.user, val)
                        conn.write("%s\n" % msg)
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
                else:
                        count = 0
                        name = conn.user.get_display_name()
                        for u in online.itervalues():
                                if u.vars['shout']:
                                        u.write_prompt(_("%s shouts: %s\n") % (name, args[0]))
                                        count += 1
                        #conn.write(_("(shouted to %d %s)\n" % (count, gettext.ngettext("player", "players", count))))
                        conn.write(gettext.ngettext("(shouted to %d player)\n", "(shouted to %d players)\n", count) % count)
                        if not conn.user.vars['shout']:
                                conn.write(_("(you are not listening to shouts)\n"))
                        
        def showlist(self, args, conn):
                if args[0] == None:
                        for cur in list.lists.itervalues():
                                conn.write('%s\n', cur.name)
                        return

                try:
                        list.lists.get(args[0]).showlist(args, conn.user)
                except KeyError:
                        conn.write(_('''\"%s\" does not match any list name.\n''' % args[0]))
                except trie.NeedMore as e:
                        conn.write(_('''Ambiguous list \"%s\". Matches: %s\n''') % (args[0], ' '.join([r.name for r in e.matches])))
                except list.ListError as e:
                        conn.write('%s\n' % e.reason)
        
        def sublist(self, args, conn):
                try:
                        list.lists.get(args[0]).sub(args, conn.user)
                except KeyError:
                        conn.write(_('''\"%s\" does not match any list name.\n''' % args[0]))
                except trie.NeedMore as e:
                        conn.write(_('''Ambiguous list \"%s\". Matches: %s\n''') % (args[0], ' '.join([r.name for r in e.matches])))
                except list.ListError as e:
                        conn.write('%s\n' % e.reason)

        def tell(self, args, conn):
                (u, ch) = self._do_tell(args, conn)
                if u != None:
                        conn.session.last_tell_user = u
                else:
                        conn.session.last_tell_ch = ch

        def uptime(self, args, conn):
                conn.write(_("Server location: %s   Server version : %s\n") % (server.location, server.version))
                conn.write(_("The server has been up since %s.\n") % time.strftime("%a %b %e, %H:%M %Z %Y", time.localtime(server.start_time)))
                conn.write(_("Up for: %s\n") % timer.hms(time.time() - server.start_time))
        
        def variables(self, args, conn):
                if args[0] == None:
                        u = conn.user
                else:
                        u = user.find.by_name_or_prefix_for_user(args[0], conn)

                if u:
                        conn.write(_("Variable settings of %s:\n\n") % u.name)
                        for var in u.vars.keys():
                                conn.write("%s=%s\n" % (var, conn.user.vars[var]))
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
                                conn.write(_('%s is no longer online.\n') % u.name)
                                u = None
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
                                        if not conn.user in ch.online:
                                                conn.user.write(_('''(You're not in channel %s.)\n''') % ch.id)
                                                ch = None
                        else:
                                u = user.find.by_name_or_prefix_for_user(args[0], conn, online_only=True)

                if ch:
                        count = ch.tell(args[1], conn.user)
                        conn.write(gettext.ngettext('(told %d player in channel %d)\n', '(told %d players in channel %d)\n', count) % (count, ch.id))
                elif u:
                        u.write_prompt('\n' + _("%s tells you: ") % conn.user.get_display_name() + args[1] + '\n')
                        conn.write(_("(told %s)") % u.name + '\n')

                return (u, ch)
        
        def who(self, args, conn):
                count = 0
                for u in online.itervalues():
                        conn.write(u.get_display_name() + '\n')
                        count = count + 1
                conn.write('\n')
                # assume plural
                #conn.write(_('%d players displayed.\n\n') % count)
                conn.write(_('%d Players Displayed.\n\n') % count)

command_list = CommandList()

class CommandParser(object):
        def run(self, s, conn):
                s = s.lstrip()
                if not checker.check_user_utf8(s):
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
                                s = alias.alias.expand(s, alias.alias.system, conn.user.aliases, conn.user)
                        except alias.AliasError:
                                conn.write(_("Command failed: There was an error expanding aliases.\n"))
                                return

                if conn.user.admin_level > admin.Level.user:
                        cmds = command_list.admin_cmds
                else:
                        cmds = command_list.cmds

                m = re.match(r'^(\S+)(?:\s+(.*))?$', s)
                cmd = None
                if m:
                        word = m.group(1).lower()
                        try:
                                cmd = cmds[word]
                        except KeyError:
                                conn.write("%s: Command not found.\n" % word)
                        except trie.NeedMore:
                                matches = cmds.all_children(word)
                                assert(len(matches) > 0)
                                if len(matches) == 1:
                                        cmd = matches[0]
                                else:
                                        conn.write("""Ambiguous command "%s". Matches: %s\n""" % (word, ' '.join([c.name for c in matches])))
                        if cmd:
                                try:
                                        cmd.run(cmd.parse_params(m.group(2)), conn)
                                except BadCommandError:
                                        cmd.help(conn)
                else:
                        #conn.write(_("Command not found.\n"))
                        assert(False)


parser = CommandParser()


# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent
