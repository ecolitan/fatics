import re
import time
import socket
import gettext

import user
import trie
import admin
import session
import var
from timer import timer
from online import online
from reload import reload
from server import server
from utf8 import checker

class InternalException(Exception):
        pass
class QuitException(Exception):
        pass
class BadCommandException(Exception):
        pass

class Command(object):
        def __init__(self, name, aliases, param_str, run, admin_level):
                self.name = name
                self.aliases = aliases
                self.param_str = param_str
                self.run = run
                self.admin_level = admin_level

        def parse_params(self, s):
                params = []
                for c in self.param_str:
                        if c in ['d', 'i', 'w', 'W']:
                                # required argument
                                if s == None:
                                        raise BadCommandException()
                                else:
                                        m = re.split(r'\s+', s, 1)
                                        assert(len(m) > 0)
                                        param = m[0]
                                        if len(param) == 0:
                                                raise BadCommandException()
                                        if c == c.lower():
                                                param = param.lower()
                                        if c in ['i', 'd']:
                                                # integer or word
                                                try:
                                                        param = int(param, 10)
                                                except ValueError:
                                                        if c == 'd':
                                                                raise BadCommandException()
                                        s = m[1] if len(m) > 1 else None
                        elif c in ['o', 'n']:
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
                                        s = m[1] if len(m) > 1 else None
                        elif c == 'S':
                                # string to end
                                if s == None or len(s) == 0:
                                        raise BadCommandException()
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
                        raise BadCommandException()
                                
                return params

        def help(self, conn):
                conn.write("help for %s\n" % self.name)

class CommandList(object):
        def __init__(self):
                # the trie data structure allows for efficiently finding
                # a command given a substring
                self.cmds = trie.Trie()
                self.admin_cmds = trie.Trie()
                self._add(Command('addplayer', [], 'WWS', self.addplayer, admin.Level.admin))
                self._add(Command('announce', [], 'S', self.announce, admin.Level.admin))
                self._add(Command('areload', [], '', self.areload, admin.Level.god))
                self._add(Command('asetadmin', [], 'wd', self.asetadmin, admin.Level.admin))
                self._add(Command('asetpasswd', [], 'wW', self.asetpasswd, admin.Level.admin))
                self._add(Command('date', [], '', self.date, admin.Level.user))

                self._add(Command('finger', ['f'], 'ooo', self.finger, admin.Level.user))
                self._add(Command('follow', [], 'w', self.follow, admin.Level.user))
                self._add(Command('help', [], 'w', self.help, admin.Level.user))
                self._add(Command('password', [], 'WW', self.password, admin.Level.user))
                self._add(Command('qtell', [], 'iS', self.qtell, admin.Level.user))
                self._add(Command('quit', [], '', self.quit, admin.Level.user))
                self._add(Command('remplayer', [], 'w', self.remplayer, admin.Level.admin))
                self._add(Command('set', [], 'wT', self.set, admin.Level.user))
                self._add(Command('shout', ['!'], 'S', self.shout, admin.Level.user))
                self._add(Command('tell', ['t'], 'nS', self.tell, admin.Level.user))
                self._add(Command('uptime', [], '', self.uptime, admin.Level.user))
                self._add(Command('vars', [], '', self.vars, admin.Level.user))
                self._add(Command('who', [], 'T', self.who, admin.Level.user))
                self._add(Command('xtell', [], 'nS', self.xtell, admin.Level.user))

        def _add(self, cmd):
                self.admin_cmds[cmd.name] = cmd
                if cmd.admin_level <= admin.Level.user:
                        self.cmds[cmd.name] = cmd
                        for a in cmd.aliases:
                                self.cmds[a] = cmd

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
                try:
                        u = user.find.by_name_exact(name)
                except user.UsernameException:
                        conn.write(_('"%s" is not a valid handle\n.') % args[0])
                else:
                        if not u:
                                conn.write(_('There is no player matching the name "%s".\n') % args[0])
                        # Note: it seems to be possible to set the admin level
                        # of a guest. I'm not sure if it's by accident or
                        # design, but I see no reason to change it.
                        elif not admin.checker.check_users(conn.user, u):
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
                try:
                        u = user.find.by_name_exact(name)
                except user.UsernameException:
                        conn.write(_('"%s" is not a valid handle\n.') % args[0])
                else:
                        if not u:
                                conn.write(_('There is no player matching the name "%s".\n') % args[0])
                        elif u.is_guest:
                                conn.write(_('You cannot set the password of an unregistered player!\n'))
                        elif not admin.checker.check_users(conn.user, u):
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
                try:
                        u = None
                        if args[0] != None:
                                if len(args[0]) < 2:
                                        conn.write(_('You need to specify at least two characters of the name.\n'))
                                else:
                                        u = user.find.by_name_or_prefix(args[0])
                                        if not u:
                                                conn.write(_('There is no player matching the name "%s".\n') % args[0])
                        else:
                                u = conn.user
                        if u:
                                conn.write(_('Finger of %s:\n\n') % u.get_display_name())
                                if u.is_online:
                                        conn.write(_('On for: %s   Idle: %s\n\n') % (u.session.get_online_time(), u.session.get_idle_time()))

                                        if u.session.use_timeseal:
                                                conn.write(_('Timeseal 1: On\n\n'))
                                        else:
                                                conn.write(_('Timeseal 1: Off\n\n'))
                                        
                                else:
                                        if u.last_logout == None:
                                                conn.write(_('%s has never connected.\n\n') % u.name)
                                        else:
                                                conn.write(_('Last disconnected: %s\n\n') % u.last_logout)
                except user.UsernameException:
                        conn.write(_('"%s" is not a valid handle\n.') % args[0])
                except user.AmbiguousException as e:
                        conn.write("""Ambiguous name "%s". Matches: %s\n""" % (args[0], ' '.join(e.names)))

        
        def follow(self, args, conn):
                conn.write('FOLLOW\n')

        def help(self, args, conn):
                conn.write('help\n')
        
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
                try:
                        u = user.find.by_name_exact(name)
                except user.UsernameException:
                        conn.write(_('"%s" is not a valid handle\n.') % args[0])
                else:
                        if not u:
                                conn.write(_("No player by the name %s is registered.\n") % name)
                        elif not admin.checker.check_users(conn.user, u):
                                conn.write(_('''You can't remove an admin with a level higher than or equal to yourself.\n'''))
                        elif u.is_online:
                                conn.write(_("A player by that name is logged in.\n"))
                        else:
                                u.remove()
                                conn.write(_("Player %s removed.\n") % name)

        def set(self, args, conn):
                [name, val] = args
                try:
                        v = var.vars[name]
                        val = v.parse_val(val)
                except KeyError:
                        conn.write(_('No such variable "%s".\n') % name)
                except var.BadVarException:
                        conn.write(_('Bad value given for variable "%s".\n') % name)
                else:
                        conn.user.set_var(name, val)
                        msg = v.get_message(val)
                        if msg:
                                conn.write("%s\n" % msg)

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
                        conn.write(_("(shouted to %d %s)\n" % (count, gettext.ngettext("player", "players", count))))
                        if not conn.user.vars['shout']:
                                conn.write(_("(you are not listening to shouts)\n"))
                        

        def tell(self, args, conn):
                u = self._do_tell(args, conn)
                conn.session.last_tell_user = u
        
        def uptime(self, args, conn):
                conn.write(_("Server location: %s   Server version : %s\n") % (server.location, server.version))
                conn.write(_("The server has been up since %s.\n") % time.strftime("%a %b %e, %H:%M %Z %Y", time.localtime(server.start_time)))
                conn.write(_("Up for: %s\n") % timer.hms(time.time() - server.start_time))
        
        def vars(self, args, conn):
                conn.write(_("Variable settings of %s:\n\n") % conn.user.name)
                for var in conn.user.vars.keys():
                        conn.write("%s=%d\n" % (var, int(conn.user.vars[var])))
                conn.write("\n")
        
        def xtell(self, args, conn):
                u = self._do_tell(args, conn)

        def _do_tell(self, args, conn):
                if args[0] == '.':
                        u = conn.session.last_tell_user
                        if not u:
                                conn.write(_("I don't know whom to tell that to.\n"))
                        elif not u.is_online:
                                conn.write(_('%s is no longer online.\n') % u.name)
                                u = None

                else:
                        try:
                                u = user.find.by_name_or_prefix(args[0])
                        except user.UsernameException:
                                conn.write(_('"%s" is not a valid handle.\n') % args[0])
                                u = None
                        else:
                                if not u:
                                        conn.write(_('There is no player matching the name "%s".\n') % args[0])
                                elif not u.is_online:
                                        conn.write(_('%s is not logged in.') % args[0])
                                        u = None

                if u:
                        #if not checker.check_user_utf8(args[1]):
                        #        conn.write(_("Your message contains one or more unprintable characters.\n"))
                        #        u = None
                        pass

                if u:
                        u.write_prompt('\n' + _("%s tells you: ") % conn.user.get_display_name() + args[1] + '\n')
                        conn.write(_("(told %s)") % u.name + '\n')

                return u
        
        def who(self, args, conn):
                count = 0
                for u in online.itervalues():
                        conn.write(u.get_display_name() + '\n')
                        count = count + 1
                conn.write('\n')
                # assume plural
                conn.write(_('%d players displayed.\n\n') % count)

command_list = CommandList()

class CommandParser(object):
        def run(self, s, conn):
                if not checker.check_user_utf8(s):
                        conn.write(_("Your command contains some unprintable characters.\n"))

                update_idle = True
                # previously the prefix '$' was used to not expand aliases
                # and '$$' was used to not update the idle time.  But these
                # options should really be orthogonal, so I made '$$' alone
                # expand aliaes. Now if you want the old behavior of neither
                # expanding aliases nor updating idle time, use '$$$'.
                if len(s) >= 2 and s[0:2] == '$$':
                        s = s[2:]
                else:
                        conn.user.session.last_command_time = time.time()

                if len(s) == 0:
                        # ignore blank line
                        return
                if s[0] == '$':
                        s = s[1:]
                else:
                        s = self.expand_aliases(s)

                if conn.user.admin_level > admin.Level.user:
                        cmds = command_list.admin_cmds
                else:
                        cmds = command_list.cmds

                m = re.match(r'^(\S+)(?:\s+(.*))?$', s)
                cmd = None
                if m:
                        word = m.group(1)
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
                                except BadCommandException:
                                        cmd.help(conn)
                else:
                        conn.write(_("Command not found.\n"))

        def expand_aliases(self, s):
                return s

parser = CommandParser()


# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent ft=python
