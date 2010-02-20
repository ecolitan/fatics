import twisted.python.rebuild

# don't reload connection because then we can't remove connections from
# the list when logging out

import admin, connection, db, session,  timer, user, command, login, telnet, timeseal, online, trie
modules = [admin, connection, db, session,  timer, user, command, login, telnet, timeseal, online, trie]

class Reload(object):
        def reload_all(self, conn):
                for mod in modules: 
                        try:
                                twisted.python.rebuild.rebuild(mod)
                        except twisted.python.rebuild.RebuildError:
                                conn.write(_("failed to reload %s\n") % mod.__name__)
                        else:
                                conn.write(_("reloaded %s\n") % mod.__name__)
reload = Reload()

# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent ft=python
