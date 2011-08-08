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

import sys

import twisted.python.rebuild

modules = ['lang','online','config','server','channel','block','bpgn','connection','variant.base_variant','variant.crazyhouse','variant.__init__','variant.chess','variant.chess960','variant.bughouse','notify','user','var','timer','utf8','match','glicko2','offer','speed_variant','partner','email','game_constants','login','history','db','seek','examine','command_parser','command.td_command','command.__init__','command.game_command','command.command','command.match_command','command.help_command','command.bug_command','command.offer_command','command.date_command','command.who_command','command.channel_command','command.message_command','command.seek_command','command.notify_command','command.news_command','command.observe_command','command.shout_command','command.examine_command','command.list_command','command.kibitz_command','command.user_command','command.admin_command','command.tell_command','command.light_command','command.var_command','admin','clock','session','timeseal','formula','game','filter_','list_','alias','telnet','reload','rating','time_format','game_list','pgn']
# left out: trie (seems to break things)
for mod in modules:
    __import__(mod)

class Reload(object):
    def reload_all(self, conn):
        # this is what http://pyunit.sourceforge.net/notes/reloading.html
        # says not to do, but as long as we don't have dependencies between
        # modules as described there, I think it's OK
        for mod in modules:
            try:
                twisted.python.rebuild.rebuild(sys.modules[mod])
            except twisted.python.rebuild.RebuildError:
                conn.write("failed to reload %s\n" % mod)
            else:
                conn.write("reloaded %s\n" % mod)
reload = Reload()

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
