import re
import time

import user
import trie
import admin
import session

class InternalException(Exception):
        pass
class QuitException(Exception):
        pass
class BadCommandException(Exception):
        pass

class Command:
        def __init__(self, name, aliases, param_str, run, adminlevel):
                self.name = name
                self.aliases = aliases
                self.param_str = param_str
                self.run = run
                self.adminlevel = adminlevel

        def parse_params(self, s):
                params = []
                for c in self.param_str:
                        if c in ['i', 'w', 'W']:
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
                                        s = m[1] if len(m) > 1 else None
                        elif c in ['o', 'n']:
                                # optional argument
                                if s == None:
                                        param = None
                                else:
                                        m = re.split(r'\s+', s, 1)
                                        assert(len(m) > 0)
                                        param = m[0].lower()
                                        assert(len(param) > 0)
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

class CommandList():
        def __init__(self):
                # the trie data structure allows for efficiently finding
                # a command given a substring
                self.cmds = trie.Trie()
                self._add(Command('addplayer', [], 'WWS', self.addplayer, admin.Level.admin))
                self._add(Command('asetpasswd', [], 'wW', self.asetpasswd, admin.Level.admin))

                self._add(Command('finger', ['f'], 'ooo', self.finger, admin.Level.user))
                self._add(Command('follow', [], 'w', self.follow, admin.Level.user))
                self._add(Command('quit', [], '', self.quit, admin.Level.user))
                self._add(Command('tell', ['t'], 'nS', self.tell, admin.Level.user))
                self._add(Command('who', [], 'T', self.who, admin.Level.user))
                self._add(Command('xtell', [], 'nS', self.xtell, admin.Level.user))

        def _add(self, cmd):
                #if cmd.adminlevel > admin.Level.user:
                self.cmds[cmd.name] = cmd
                for a in cmd.aliases:
                        self.cmds[a] = cmd

        def addplayer(self, args, conn):
                [name, email, real_name] = args
                try:
                        u = user.find.by_name(name)
                except user.UsernameException as e:
                        conn.write(e.reason + '\n')
                else:
                        if u:
                                conn.write(_('A player named %s is already registered.\n') % name)
                        else:
                                passwd = user.create.passwd()
                                user.create.new(name, email, passwd, real_name)
                                conn.write(_('Added: >%s< >%s< >%s< >%s<\n') % (name, real_name, email, passwd))


        def asetpasswd(self, args, conn):
                [name, passwd] = args
                try:
                        u = user.find.by_name(name)
                except user.UsernameException:
                        conn.write(_('"%s" is not a valid handle\n.') % args[0])
                else:
                        if not u:
                                conn.write(_('There is no player matching the name "%s".\n') % args[0])
                        elif u.is_guest:
                                conn.write(_('You cannot set the password of an unregistered player!\n'))
                        elif not user.is_legal_passwd(passwd):
                                conn.write(_('"%s" is not a valid password.\n') % passwd)
                        else:
                                u.set_passwd(passwd)
                                conn.write(_('Password of %s changed to %s.\n') % (name, '*' * len(passwd)))
                                if u.is_online:
                                        u.session.conn.write(_('\n%s has changed your password.\n') % conn.user.name)

        def finger(self, args, conn):
                try:
                        u = None
                        if args[0] != None:
                                if len(args[0]) < 2:
                                        conn.write(_('You need to specify at least two characters of the name.\n'))
                                else:
                                        u = user.find.by_name(args[0], min_len=2)
                                        if not u:
                                                u = user.find.by_prefix(args[0])
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
                        conn.write("""Ambiguous name "%s". Matches: %s\n""" % (args[0], ' '.join([dbu['user_name'] for dbu in e.users])))

        
        def follow(self, args, conn):
                conn.write('FOLLOW')
        
        def quit(self, args, conn):
                raise QuitException()

        def tell(self, args, conn):
                u = self._do_tell(args, conn)
                conn.session.last_tell_user = u
        
        def xtell(self, args, conn):
                u = self._do_tell(args, conn)

        def _do_tell(self, args, conn):
                if args[0] == '.':
                        u = conn.session.last_tell_user
                        if not u:
                                conn.write(_("I don't know who to tell that to.\n"))
                        elif not u.is_online:
                                conn.write(_('"%s" is no longer online.\n') % args[0])
                                u = None

                else:
                        try:
                                u = user.find.by_name(args[0])
                        except user.UsernameException:
                                conn.write(_('"%s" is not a valid handle.\n') % args[0])
                        else:
                                if not u:
                                        conn.write(_('There is no player matching the name "%s".\n') % args[0])
                                elif not u.is_online:
                                        conn.write(_('%s is not logged in.') % args[0])
                                        u = None

                if u:
                        u.write('\n' + _("%s tells you: ") % conn.user.get_display_name() + args[1] + '\n')
                        conn.write(_("(told %s)") % u.name + '\n')

                return u
        
        def who(self, args, conn):
                count = 0
                for s in session.online.values():
                        conn.write(s.user.get_display_name() + '\n')
                        count = count + 1
                conn.write('\n')
                # assume plural
                conn.write(_('%d players displayed.\n\n') % count)

command_list = CommandList()

def handle_command(s, conn):
        conn.user.session.last_command_time = time.time()
        m = re.match(r'^(\S+)(?:\s+(.*))?$', s)
        cmd = None
        if m:
                word = m.group(1)
                try:
                        cmd = command_list.cmds[word]
                except KeyError:
                        conn.write("%s: Command not found.\n" % word)
                except trie.NeedMore:
                        matches = command_list.cmds.all_children(word)
                        assert(len(matches) > 0)
                        if len(matches) == 1:
                                cmd = matches.pop()
                        else:
                                conn.write("""Ambiguous command "%s". Matches: %s\n""" % (word, ' '.join([c.name for c in matches])))
                if cmd:
                        try:
                                cmd.run(cmd.parse_params(m.group(2)), conn)
                        except BadCommandException:
                                cmd.help(conn)
        else:
                conn.write("Command not found.\n")


# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent ft=python
