# -*- coding: utf-8 -*-
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

from game_command import GameMixin

from command import *

class KibitzCommand(Command):
    def _do_kibitz(self, g, msg, conn):
        name = conn.user.get_display_name()
        plist = g.players | g.observers
        if g.bug_link:
            plist |= g.bug_link.players | g.bug_link.observers
        assert(len(plist) > 0)
        count = 0
        rat = conn.user.get_rating(g.speed_variant)
        for u in plist:
            if not u.vars['kibitz']:
                continue
            if (u.vars['kiblevel'] and int(rat) < u.vars['kiblevel']
                    and not conn.user.is_admin()):
                continue
            if (conn.user.name in u.censor
                    and not conn.user.is_admin()):
                continue
            if u != conn.user:
                count += 1
            u.write_('\n%s(%s)[%d] kibitzes: %s\n',
                (name, rat, g.number, msg))
        conn.write(ngettext('(kibitzed to %d player)\n',
            '(kibitzed to %d players)\n', count) % count)

class WhisperCommand(Command):
    def _do_whisper(self, g, msg, conn):
        name = conn.user.get_display_name()
        count = 0
        rat = conn.user.get_rating(g.speed_variant)
        plist = g.observers
        if g.bug_link:
            plist |= g.bug_link.observers
        if g.gtype == game.EXAMINED:
            plist |= g.players
        for u in plist:
            if (u.vars['kiblevel'] and int(rat) < u.vars['kiblevel']
                    and not conn.user.is_admin()):
                continue
            if (conn.user.name in u.censor
                    and not conn.user.is_admin()):
                continue
            if u != conn.user:
                count += 1
            u.write_('\n%s(%s)[%d] whispers: %s\n',
                (name, rat, g.number, msg))
        conn.write(ngettext('(whispered to %d player)\n',
            '(whispered to %d players)\n', count) % count)

@ics_command('kibitz', 'S', admin.Level.user)
class Kibitz(KibitzCommand, GameMixin):
    def run(self, args, conn):
        g = self._game_param(None, conn)
        if not g:
            return
        if conn.user.is_guest and conn.user not in g.players:
            conn.write(_("Only registered players may kibitz to others' games."))
            return
        self._do_kibitz(g, args[0], conn)

@ics_command('whisper', 'S', admin.Level.user)
class Whisper(WhisperCommand, GameMixin):
    def run(self, args, conn):
        g = self._game_param(None, conn)
        if not g:
            return
        if conn.user.is_guest and conn.user not in g.players:
            conn.write(_("Only registered players may whisper to others' games."))
            return
        self._do_whisper(g, args[0], conn)

@ics_command('xkibitz', 'iS')
class Xkibitz(KibitzCommand):
    def run(self, args, conn):
        g = game.from_name_or_number(args[0], conn)
        if g:
            self._do_kibitz(g, args[1], conn)

@ics_command('xwhisper', 'iS')
class Xwhisper(WhisperCommand):
    def run(self, args, conn):
        g = game.from_name_or_number(args[0], conn)
        if g:
            self._do_whisper(g, args[1], conn)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
