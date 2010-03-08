import time
import re

import alias
import utf8
import trie
import admin
import command

class CommandParser(object):
    def parse(self, s, conn):
        #s = s.lstrip()
        s = s.strip()

        if len(conn.user.session.games) > 0:
            if conn.user.session.games.values()[0].variant.do_move(s, conn):
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
                s = alias.alias.expand(s, alias.alias.system, conn.user.aliases, conn.user)
            except alias.AliasError:
                conn.write(_("Command failed: There was an error expanding aliases.\n"))
                return

        if conn.user.admin_level > admin.Level.user:
            cmds = command.command_list.admin_cmds
        else:
            cmds = command.command_list.cmds

        m = re.match(r'^(\S+)(?:\s+(.*))?$', s)
        cmd = None
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
                    cmd.run(cmd.parse_args(m.group(2)), conn)
                except command.BadCommandError:
                    cmd.help(conn)
        else:
            #conn.write(_("Command not found.\n"))
            assert(False)

parser = CommandParser()

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
