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

import random
import time
import datetime

import user
import rating
import timeseal
import speed_variant
import clock
import history
import time_format
import variant

from db import db
from online import online
from game_constants import *

games = {}

def find_free_slot():
    """Find the first available game number."""
    # This is O(n) in the number of games, but it's simple and should
    # be more than efficient enough.
    i = 1
    while True:
        if i not in games:
            return i
        i += 1

def from_name_or_number(arg, conn):
    g = None
    try:
        num = int(arg)
        if num in games:
            g = games[num]
        else:
            conn.write(_("There is no such game.\n"))
    except ValueError:
        # user name
        u = user.find_by_prefix_for_user(arg, conn, online_only=True)
        if u:
            if not u.session.game:
                conn.write(_("%s is not playing or examining a game.\n")
                    % u.name)
            else:
                g = u.session.game
    return g

class Game(object):
    def __init__(self):
        """ Common setup for examined and played games.  Assumes
        self.players is already set. """
        self.number = find_free_slot()
        games[self.number] = self
        self.observers = set()
        self.pending_offers = []
        self.bug_link = None

        # (silently) remove each player's seeks
        for p in self.players:
            for s in p.session.seeks[:]:
                s.remove()

        # notify partner, if any
        for p in self.players:
            if p.session.partner:
                if self.gtype == PLAYED:
                    p.session.partner.write_('\nYour partner has joined a game with %s.\n', (self.get_opp(p),))
                else:
                    p.session.partner.write_('\nYour partner has started examining a game.\n')

        # remove offers to and from each player
        for p in self.players:
            for off in p.session.offers_sent[:]:
                if off.name == 'match offer':
                    assert(off.a == p)
                    if self.gtype == PLAYED:
                        # original fics says "has joined a match with"
                        off.b.write_('\n%(pname)s, who was challenging you, has joined a game with %(oname)s.\n',
                            {'pname': p.name, 'oname': self.get_opp(p)})
                    else:
                        assert(self.gtype == EXAMINED)
                        off.b.write_('\n%(pname)s, who was challenging you, has started examining a game.\n',
                            {'pname': p.name})
                    p.write_('Challenge to %s withdrawn.\n', (off.b.name,))
                    off.b.write_('Challenge from %s removed.\n',
                        (p.name,))
                    if off.variant_name == 'bughouse':
                        # inform the other two players involved in the
                        # withdrawn bughouse match offer
                        assert(p.session.partner)
                        assert(off.b.session.partner)
                        if self.gtype == PLAYED:
                            off.b.session.partner.write_('\n%(pname)s, who was challenging your partner, has joined a game with %(oname)s.\n',
                                {'pname': p.name,
                                'oname': self.get_opp(p).name})
                        else:
                            off.b.session.partner.write_('\n%(pname)s, who was challenging your partner, has started examining a game.\n', (p.name,))
                        p.session.partner.write_("Partner's challenge to %s withdrawn.\n", (off.b.name,))
                        off.b.session.partner.write_("Partner's challenge from %s removed.\n", (p.name,))
                    off.withdraw(notify=False)

            for off in p.session.offers_received[:]:
                if off.name == 'match offer':
                    if self.gtype == PLAYED:
                        assert(off.b == p)
                        off.a.write_('\n%(pname)s, whom you were challenging, has joined a game with %(oname)s.\n',
                            {'pname': p.name, 'oname': self.get_opp(p)})
                    else:
                        assert(self.gtype == EXAMINED)
                        off.a.write_('\n%(pname)s, whom you were challenging, has started examining a game.\n',
                            {'pname': p.name})
                    p.write_('Challenge from %s removed.\n', (off.a.name,))
                    off.a.write_('Challenge to %s withdrawn.\n', (p.name,))
                    if off.variant_name == 'bughouse':
                        # inform the other two players involved in the declined
                        # bughouse match offer
                        assert(p.session.partner)
                        assert(off.a.session.partner)
                        if self.gtype == PLAYED:
                            off.a.session.partner.write_('\n%(pname)s, whom your partner was challenging, has joined a game with %(oname)s.\n',
                                {'pname': p.name,
                                'oname': self.get_opp(p).name})
                        else:
                            off.a.session.partner.write_('\n%s, whom your partner was challenging, has started examining a game.\n', (p.name,))
                        p.session.partner.write_("Partner's challenge from %s removed.\n", (off.a.name,))
                        off.a.session.partner.write_("Partner's challenge to %s withdrawn.\n", (p.name,))
                    off.decline(notify=False)

            # if the player has a partner, also notify about bughouse
            # challenges to or from the partner
            if p.session.partner:
                for off in p.session.partner.session.offers_sent[:]:
                    if off.variant_name == 'bughouse':
                        if self.gtype == PLAYED:
                            off.b.write_('\n%(pname)s, whose partner was challenging you, has joined a game with %(oname)s.\n',
                                {'pname': p.name,
                                'oname': self.get_opp(p).name})
                            # original FICS says "whose partner challenged your partner"
                            off.b.session.partner.write_('\n%(pname)s, whose partner was challenging your partner, has joined a game with %(oname)s.\n',
                                {'pname': p.name,
                                'oname': self.get_opp(p).name})
                        else:
                            off.b.write_('\n%s, whose partner was challenging you, has started examining a game.\n', (p.name,))
                            off.b.session.partner.write_('\n%s, whose partner was challenging your partner, has started examining a game.\n', (p.name,))
                        p.session.partner.write_("Challenge to %s withdrawn.\n", (off.b.name,))
                        off.b.write_('Challenge from %s removed.\n', (p.session.partner.name,))
                        off.b.session.partner.write_("Partner's challenge from %s removed.\n", (off.a.name,))
                        p.write_("Partner's challenge to %s withdrawn.", (off.b.name,))
                        off.withdraw(notify=False)

                for off in p.session.partner.session.offers_received[:]:
                    if off.variant_name == 'bughouse':
                        if self.gtype == PLAYED:
                            off.a.write_('\n%(pname)s, whose partner you were challenging, has joined a game with %(oname)s.\n',
                                {'pname': p.name,
                                'oname': self.get_opp(p).name})
                            # original FICS says "(potential opponent)'s partner has joined a game with...."
                            off.a.session.partner.write_('\n%(pname)s, whose partner your partner was challenging, has joined a game with %(oname)s.\n',
                                {'pname': p.name,
                                'oname': self.get_opp(p).name})
                        else:
                            off.a.write_('\n%(pname)s, whose partner you were challenging, has started examining a game.\n', (p.name,))
                            off.a.session.partner.write_('\n%(pname)s, whose partner your partner was challenging, has started examining a game.\n', (p.name,))
                        off.a.write_("Challenge to %s withdrawn.\n", (p.session.partner.name,))
                        off.a.session.partner.write_("Partner's challenge to %s withdrawn.\n", (p.session.partner.name,))
                        p.session.partner.write_("Challenge from %s removed.\n", (off.a.name,))
                        p.write_("Partner's challenge from %s removed.", (off.a.name,))
                        off.decline(notify=False)

    def send_boards(self):
        for p in self.players:
            self.send_board(p)
        for u in self.observers:
            self.send_board(u)

    def send_board(self, u, isolated=False):
        if u.vars['style'] == 12:
            if (self.gtype == PLAYED and self.variant.name == 'chess' and
                    u.session.ivars['compressmove'] and
                    self.variant.pos.get_last_move() is not None and
                    not isolated):
                u.write_nowrap(self.variant.to_deltaboard(u))
            else:
                u.write_nowrap(self.variant.to_style12(u))
        else:
            # style 1, the default
            u.write_nowrap(self.variant.to_style1(u))

    def __eq__(self, other):
        return self.number == other.number

    def __hash__(self):
        return self.number

    def next_move(self, mv, conn):
        self.send_boards()

    def get_user_side(self, user):
        if user == self.white:
            return WHITE
        elif user == self.black:
            return BLACK
        else:
            raise RuntimeError('Game.get_side(): got a non-player')

    def get_side_user(self, side):
        if side == WHITE:
            return self.white
        else:
            return self.black

    def get_opp(self, user):
        side = self.get_user_side(user)
        return self.get_side_user(opp(side))

    def get_user_to_move(self):
        if self.variant.get_turn() == WHITE:
            return self.white
        else:
            return self.black

    def observe(self, u):
        assert(u not in self.observers)
        u.session.observed.add(self)
        self.observers.add(u)
        u.write(_('You are now observing game %d.\n') % self.number)
        self.send_info_str(u)
        self.send_board(u, isolated=True)

    def send_info_str(self, u):
        u.write('Game %d: %s\n' % (self.number, self.info_str))

    def unobserve(self, u):
        """Remove the given user as an observer and notify the user."""
        assert(u in self.observers)
        u.write_('\nRemoving game %d from observation list.\n',
            self.number)
        u.session.observed.remove(self)
        self.observers.remove(u)

    def free(self):
        for o in self.pending_offers[:]:
            o.decline(notify=False)
        assert(not self.pending_offers)
        for u in self.observers.copy():
            self.unobserve(u)
        assert(not self.observers)
        del games[self.number]

    def get_eco(self):
        i = min(self.variant.pos.ply, 36)
        row = None
        while i >= self.variant.pos.start_ply:
            hash_ = self.variant.pos.history.get_hash(i)
            row = db.get_eco(hash_)
            if row:
                break
            i -= 1
        if row:
            ret = (i, row['eco'], row['long_'])
        else:
            ret = (0, 'A00', 'Unknown')
        return ret

    def get_nic(self):
        i = min(self.variant.pos.ply, 36)
        row = None
        while i >= self.variant.pos.start_ply:
            hash_ = self.variant.pos.history.get_hash(i)
            row = db.get_nic(hash_)
            if row:
                break
            i -= 1
        if row:
            ret = (i, row['nic'])
        else:
            ret = (0, '-----')
        return ret

    def get_movetext(self):
        i = self.variant.pos.start_ply
        moves = []
        while i < self.variant.pos.ply:
            mv = self.variant.pos.history.get_move(i)
            moves.append(mv.to_san())
            i += 1
        ret = ' '.join(moves)
        return ret

    def get_ply_count(self):
        return self.variant.pos.ply - self.variant.pos.start_ply

    def write_moves(self, conn):
        # don't translate since clients parse these messages
        conn.write("\nMovelist for game %d:\n\n" % self.number)

        time_str = conn.user.format_datetime(self.when_started)
        #self.when_started.strftime("%a %b %e, %H:%M %Z %Y")

        # Original FICS prints (UNR) for unrated players here; in other
        # places it usually uses (++++) or (----) instead.  This looks like
        # gratuitous inconsistency to me, so let's see if we can get
        # away with using the same notation everywhere.
        conn.write("%s (%s) vs. %s (%s) --- %s\n" % (self.white_name,
            self.white_rating, self.black_name, self.black_rating, time_str))

        conn.write("%s %s match, initial time: %d minutes, increment: %d seconds.\n\n" %
            (self.rated_str.capitalize(), self.speed_variant,
                self.white_time, self.inc))
        conn.write('Move  %-23s %s\n----  ---------------------   ---------------------\n' % (self.white_name, self.black_name))
        i = self.variant.pos.start_ply & ~1
        while i < self.variant.pos.ply:
            if i < self.variant.pos.start_ply:
                move_str = '...'
            else:
                mv = self.variant.pos.history.get_move(i)
                move_str = '%-7s (%s)' % (mv.to_san(),
                    time_format.hms(mv.time, conn.user))
            if i % 2 == 0:
                conn.write('%3d.  %-23s ' % (int((i + 3) / 2),move_str))
            else:
                assert(len(move_str) <= 23)
                conn.write('%s\n' % move_str)
            i += 1

        if i & 1 != 0:
            conn.write('\n')

        conn.write('      {Still in progress} *\n\n')

    def parse_move(self, s, conn):
        try:
            mv = self.variant.parse_move(s, conn)
            parsed = mv is not None
            illegal = False
        except variant.base_variant.IllegalMoveError:
            illegal = True
            parsed = True
        if parsed:
            if self.gtype == PLAYED and (
                    self.get_user_side(conn.user) != self.variant.get_turn()):
                conn.write(_('It is not your move.\n'))
            elif illegal:
                conn.write(_('Illegal move (%s).\n') % s)
                # Re-send the board in case of an illegal move.
                # Eboard depends on this if legality checking is off.
                self.send_board(conn.user, True)
            else:
                self.variant.do_move(mv)
                self.next_move(mv, conn)
        return parsed

    def ginfo(self, conn):
        conn.write(_('Game %d: Game information.\n\n') % self.number)
        if self.gtype == PLAYED:
            conn.write(_('  %s (%s) vs %s (%s) %s %s game.\n') % (
                self.white_name, self.white_rating, self.black_name,
                self.black_rating, self.rated_str, self.speed_variant))
            # XXX display something different for non-fischer clocks?
            conn.write(_('  Time controls: %d %d\n') %
                (60 * self.white_time, self.inc))
            conn.write(_('  Time of starting: %s\n') %
                conn.user.format_datetime(self.when_started))
            conn.write(_('   White time %s    Black time %s\n') %
                (time_format.hms(self.clock.get_white_time(), conn.user),
                time_format.hms(self.clock.get_black_time(), conn.user)))
            conn.write(_('  The clock is not paused\n'))
        else:
            assert(self.gtype == EXAMINED)
            white_name = list(self.players)[0].name
            black_name = white_name
            exname = white_name
            # XXX use history names when available
            # original FICS omits additional examiners too
            conn.write(_('  %(exname)s is examining %(wname)s vs %(bname)s.\n') %
                {'exname': exname, 'wname': white_name, 'bname': black_name})

        # stuff hidden by private (if it is implemented)
        hm = self.variant.pos.ply
        fifty = self.variant.pos.fifty_count
        # XXX this is printed even for zh and bug, which do not use
        # the fifty-move count
        conn.write(ngettext('  %d halfmove has been made.\n',
            '  %d halfmoves have been made.\n', hm) % hm)
        conn.write(ngettext(
            '  Fifty move count started at halfmove %(start)d (%(left)d halfmove until a draw).\n',
            '  Fifty move count started at halfmove %(start)d (%(left)d halfmoves until a draw).\n', 100 - fifty) % {'start': hm - fifty, 'left': 100 - fifty})
        w_oo = self.variant.pos.check_castle_flags(True, True)
        w_ooo = self.variant.pos.check_castle_flags(True, False)
        b_oo = self.variant.pos.check_castle_flags(False, True)
        b_ooo = self.variant.pos.check_castle_flags(False, False)
        if w_oo and w_ooo:
            conn.write(_('  White may castle both kingside and queenside.\n'))
        elif w_oo:
            conn.write(_('  White may castle kingside.\n'))
        elif w_ooo:
            conn.write(_('  White may castle queenside.\n'))
        else:
            conn.write(_('  White may not castle.\n'))
        if b_oo and b_ooo:
            conn.write(_('  Black may castle both kingside and queenside.\n'))
        elif b_oo:
            conn.write(_('  Black may castle kingside.\n'))
        elif b_ooo:
            conn.write(_('  Black may castle queenside.\n'))
        else:
            conn.write(_('  Black may not castle.\n'))
        # This is different from original FICS in that we only report
        # the double-push if there is a pseudo-legal en passant capture.
        if self.variant.pos.ep:
            conn.write(_('  Double pawn push occurred on the %s-file.\n') %
                'abcdefgh'[file(self.variant.pos.ep)])
        else:
            conn.write(_("  Double pawn push didn't occur.\n"))


class PlayedGame(Game):
    def __init__(self, chal):
        self.gtype = PLAYED

        if chal.adjourned:
            self._resume(chal.adjourned, chal.a, chal.b)
            creating = 'Continuing'
        else:
            self._init_new(chal)
            creating = 'Creating'
        assert(self.clock)
        self.is_active = True

        self.players = set([self.white, self.black])
        super(PlayedGame, self).__init__()

        self.flip = False
        self.private = False
        self.rated_str = 'rated' if self.rated else 'unrated'

        # GuestBEZD (++++) admin (1000) unrated blitz 2 12
        self.info_str = '%s (%s) %s (%s) %s %s %d %d' % (
            self.white_name, self.white_rating, self.black_name,
            self.black_rating, self.rated_str, self.speed_variant,
            self.white_time, self.inc)
        # it seems original FICS uses "creating" here even for
        # adjourned games
        create_str = '\nCreating: %s' % self.info_str
        self.white.write_nowrap(create_str)
        self.black.write_nowrap(create_str)

        create_str_2 = '\n{Game %d (%s vs. %s) %s %s %s match.}\n' % (
            self.number, self.white_name, self.black_name, creating,
            self.rated_str, self.speed_variant)
        self.white.write_nowrap(create_str_2)
        self.black.write_nowrap(create_str_2)

        # The order of fields FICS sends differs from the
        # "help iv_gameinfo" documentation; the it= field gives
        # the initial time increment for white, and the i= field
        # does the same for black.  This seems wrong since "it" was
        # supposed to stand for "initial time", but compatability
        # with FICS is more important than being logical.
        # not sure about the m and n; maybe they are a version number?
        # TODO: add info about clock style, variant/speed to gameinfo string
        if self.speed_variant.variant.name == 'chess':
            vname = self.speed_variant.speed.name
        else:
            # XXX how do we convey the speed and variant, when the current
            # format only gives one field?
            vname = self.speed_variant.variant.name
        self.gameinfo_str = '\n<g1> %d p=%d t=%s r=%d u=%d,%d it=%d,%d i=%d,%d pt=0 rt=%s,%s ts=%d,%d m=2 n=0\n' % (self.number, self.private, vname, self.rated, self.white.is_guest, self.black.is_guest, self.initial_secs, self.inc, self.initial_secs, self.inc, self.white_rating.gameinfo_str(), self.black_rating.gameinfo_str(), self.white.has_timeseal(), self.black.has_timeseal())
        if self.white.session.ivars['gameinfo']:
            self.white.write_nowrap(self.gameinfo_str)
        if self.black.session.ivars['gameinfo']:
            self.black.write_nowrap(self.gameinfo_str)

        self.variant = speed_variant.variant_class[self.speed_variant.variant.name](self)
        # play the stored moves for an adjourned game
        if chal.adjourned:
            moves = chal.adjourned['movetext'].split(' ')
            assert(len(moves) == chal.adjourned['ply_count'])
            for san_mv in moves:
                mv = self.variant.pos.move_from_san(san_mv)
                mv.time = 0.0 # XXX
                self.variant.do_move(mv)

        assert(self.white.session.game is None)
        assert(self.black.session.game is None)
        self.white.session.game = self
        self.black.session.game = self

        self.white.session.last_opp = self.black
        self.black.session.last_opp = self.white

        gnotified = set()
        for p in self.players:
            for uf in p.session.followed_by:
                uf.write_('\n%(uname)s, whom you are following, has started a game with %(oppname)s.\n',
                    {'uname': p, 'oppname': self.get_opp(p)})
                self.observe(uf)

            gnotified |= p.gnotified

        # don't notify players of this game themselves
        gnotified -= set([p.name for p in self.players])

        # notify players, unless they are one of the players of this game
        for un in gnotified:
            u = online.find_exact(un)
            if u:
                # using info_str doesn't quite work, since original
                # fics inserts "vs." into the game notification
                #u.write_('\nGame notification: %s: Game %d\n' % (
                #    self.info_str, self.number))
                u.write('\nGame notification: %s (%s) vs. %s (%s) %s %s %d %d: Game %d\n' % (
                    self.white_name, self.white_rating, self.black_name,
                    self.black_rating, self.rated_str, self.speed_variant,
                    self.white_time, self.inc, self.number))

        # notify users with the gin variable set
        for u in online.gin_var:
            u.write_nowrap(create_str_2)

        p = self.get_user_to_move()
        if p.has_timeseal():
            p.session.ping(for_move=True)
        self.send_boards()

    def _resume(self, adj, a, b):
        """ Resume an adjourned game. """
        if adj['white_user_id'] == a.id:
            assert(adj['black_user_id'] == b.id)
            self.white = a
            self.black = b
        else:
            assert(adj['white_user_id'] == b.id)
            assert(adj['black_user_id'] == a.id)
            self.white = b
            self.black = a
        self.white_name = self.white.name
        self.black_name = self.black.name

        self.speed_variant = speed_variant.from_names(adj['speed_name'],
            adj['variant_name'])
        self.white_time = adj['time']
        self.black_time = adj['time']
        # XXX is this correct, or should we use the actual time
        # remaining for the gameinfo string?
        if self.white_time == 0:
            self.initial_secs = 10.0
        else:
            self.initial_secs = 60.0 * self.white_time
        # XXX use a stored rating?
        self.white_rating = self.white.get_rating(self.speed_variant)
        self.black_rating = self.black.get_rating(self.speed_variant)
        self.inc = adj['inc']
        self.rated = adj['rated']
        self.tags = {
            'time': adj['time'],
            'inc': adj['inc']
        }
        self.clock_name = adj['clock_name']
        self.clock = clock.clock_names[self.clock_name](self,
            adj['white_clock'], adj['black_clock'])
        self.idn = adj['idn'] # for chess960
        if self.clock_name == 'overtime':
            self.overtime_move_num = adj['overtime_move_num']
            self.overtime_bonus = adj['overtime_bonus']
        self.when_started = adj['when_started']

        # clear the game in the database
        db.delete_adjourned(adj['adjourn_id'])

    def _init_new(self, chal):
        side = chal.side
        if side is None:
            side = self._pick_color(chal.a, chal.b)
        if side == WHITE:
            self.white = chal.a
            self.black = chal.b
        else:
            assert(side == BLACK)
            self.white = chal.b
            self.black = chal.a
        self.white_name = self.white.name
        self.black_name = self.black.name

        self.speed_variant = chal.speed_variant
        self.white_rating = self.white.get_rating(self.speed_variant)
        self.black_rating = self.black.get_rating(self.speed_variant)
        self.white_time = chal.time
        self.black_time = chal.time
        self.inc = chal.inc
        self.tags = {
            'time': chal.time,
            'inc': chal.inc
        }
        if self.speed_variant.variant.name == 'chess960':
            if chal.idn is not None:
                if chal.idn == -1:
                    # special value to force a random choice
                    self.idn = random.randint(0, 959)
                else:
                    self.idn = chal.idn
            else:
                self.idn = self._pick_idn(chal.a, chal.b)
        else:
            self.idn = None
        if chal.clock_name == 'overtime':
            self.overtime_move_num = chal.overtime_move_num
            self.overtime_bonus = chal.overtime_bonus

        self.rated = chal.rated

        if self.white_time == 0:
            self.initial_secs = 10.0
        else:
            self.initial_secs = 60.0 * self.white_time

        self.clock_name = chal.clock_name
        self.clock = clock.clock_names[chal.clock_name](self,
            self.initial_secs, self.initial_secs)
        self.when_started = datetime.datetime.utcnow()

    def _pick_color(self, a, b):
        """ Choose the color allocation for two players by comparing the
        colors of games in their history.  Returns the color for player a.
        """
        ahist = a.get_history()
        bhist = b.get_history()
        for i in range(1, 12):
            if i > len(ahist):
                if i > len(bhist):
                    # end of history for both players; choose randomly
                    return random.choice([WHITE, BLACK])
                # end of a's history; give b the opposite of this entry
                return self._color_from_char(bhist[-i]['color_char'])
            elif i > len(bhist):
                # end of b's history; give a the opposite of this entry
                return opp(self._color_from_char(ahist[-i]['color_char']))

            if ahist[-i]['color_char'] != bhist[-i]['color_char']:
                # players had opposite colors, so swap them for this game
                return self._color_from_char(bhist[-i]['color_char'])

            # otherwise players had like colors, so continue searching

        # unreached
        assert(False)

    def _pick_idn(self, a, b):
        """ Choose an idn for a chess960 game, either by repeating the
        previous idn if this is a rematch or choosing randomly. """
        ahist = a.get_history()
        bhist = b.get_history()
        idn = None
        if ahist and bhist:
            if (ahist[-1]['opp_name'] == b.name and
                    bhist[-1]['opp_name'] == a.name):
                # this is a rematch
                assert(ahist[-1]['idn'] == bhist[-1]['idn'])
                if ahist[-1]['idn'] is not None:
                    # try to use the same initial setup for the rematch,
                    # unless we have already done so (don't use the same
                    # position 3 times in a row)
                    if (len(ahist) < 2 or len(bhist) < 2 or not
                            (ahist[-2]['opp_name'] == b.name and
                            bhist[-2]['opp_name'] == a.name and
                            ahist[-2]['idn'] == ahist[-1]['idn'])):
                        idn = ahist[-1]['idn']
        if idn is None:
            # pick a random position
            idn = random.randint(0, 959)
        return idn

    def _color_from_char(self, char):
        assert(char in ['W', 'B'])
        return WHITE if char == 'W' else BLACK

    def next_move(self, mv, conn):
        # decline all offers to the player who just moved
        u = self.get_user_to_move()
        offers = [o for o in self.pending_offers if o.a == u]
        for o in offers:
            o.decline()

        time = 0.0
        if self.is_active and self.variant.pos.ply > 1:
            moved_side = opp(self.variant.get_turn())
            if self.clock.is_ticking:
                if conn.user.has_timeseal():
                    assert(conn.session.move_sent_timestamp is not None)
                    elapsed_ms = (conn.session.timeseal_last_timestamp -
                        conn.session.move_sent_timestamp)
                    time = self.clock.got_move(moved_side,
                        self.variant.pos.ply, elapsed_ms / 1000.0)
                    mv.lag = int(round(1000.0 * self.clock.real_elapsed -
                        elapsed_ms))
                else:
                    time = self.clock.got_move(moved_side,
                        self.variant.pos.ply)
            if self.get_user_to_move().vars['autoflag']:
                self.clock.check_flag(self, moved_side)
            if self.is_active:
                if self.variant.pos.ply > 2:
                    self.clock.add_increment(moved_side)
                self.clock.start(self.variant.get_turn())

        assert(mv == self.variant.pos.get_last_move())
        mv.time = time

        p = self.get_user_to_move()
        if p.has_timeseal():
            p.session.ping(for_move=True)
        super(PlayedGame, self).next_move(mv, conn)

        if self.variant.name == "bughouse":
            # bughouse is a special case because a checkmate or stalemate
            # on one board doesn't necessariy end the games
            if self.variant.pos.is_checkmate:
                if (self.variant.pos.is_contact_or_knight_mate
                        or self.bug_link.variant.pos.is_stalemate):
                    # mate, and the linked game can never provide a piece
                    # to stop it
                    if self.variant.get_turn() == WHITE:
                        self.result('%s checkmated' % self.white_name, '0-1')
                    else:
                        self.result('%s checkmated' % self.black_name, '1-0')
                elif self.bug_link.variant.pos.is_checkmate:
                    # linked game is also a mate.  If the mating players are on
                    # the same team, that team wins; otherwise it's a draw.
                    # A contact or N mate would have already ended this game.
                    assert(not self.bug_link.variant.pos.is_contact_or_knight_mate)
                    if self.bug_link.variant.get_turn() != self.variant.get_turn():
                        self.is_active = False
                        if self.variant.get_turn() == WHITE:
                            self.bug_link.result('%s and %s checkmated' % (self.bug_link.black_name, self.white_name), '1-0')
                            self.result('%s and %s checkmated' % (self.bug_link.black_name, self.white_name), '0-1')
                        else:
                            self.bug_link.result('%s and %s checkmated' % (self.bug_link.white_name, self.black_name, '0-1'))
                            self.result('%s and %s checkmated' % (self.bug_link.white_name, self.black_name), '1-0')
                    else:
                        self.is_active = False
                        self.bug_link.result('Game drawn by mate on both boards', '1/2-1/2')
                        self.result('Game drawn by mate on both boards', '1/2-1/2')
            elif self.variant.pos.is_stalemate:
                if self.bug_link.variant.pos.is_stalemate:
                    self.is_active = False
                    self.bug_link.result('Game drawn by stalemate', '1/2-1/2')
                    self.result('Game drawn by stalemate', '1/2-1/2')
                elif self.bug_link.variant.pos.is_checkmate:
                    if self.bug_link.variant.get_turn() == WHITE:
                        self.bug_link.result('%s checkmated'
                            % self.bug_link.white_name, '0-1')
                    else:
                        self.bug_link.result('%s checkmated'
                            % self.bug_link.black_name, '1-0')
        else:
            if self.variant.pos.is_checkmate:
                if self.variant.get_turn() == WHITE:
                    self.result('%s checkmated' % self.white_name, '0-1')
                else:
                    self.result('%s checkmated' % self.black_name, '1-0')
            elif self.variant.pos.is_stalemate:
                self.result('Game drawn by stalemate', '1/2-1/2')
            elif self.variant.pos.is_draw_nomaterial:
                self.result('Neither player has mating material', '1/2-1/2')

    def observe(self, u):
        """ For some reason it seems that FICS only sends gameinfo strings
        for played games, not examined games. """
        super(PlayedGame, self).observe(u)
        if u.session.ivars['gameinfo']:
            u.write(self.gameinfo_str)

    def result(self, msg, result_code):
        self.when_ended = datetime.datetime.utcnow()
        line = '\n{Game %d (%s vs. %s) %s} %s\n' % (self.number,
            self.white_name, self.black_name, msg, result_code)
        self.white.write_nowrap(line)
        self.black.write_nowrap(line)
        for u in self.observers:
            u.write_nowrap(line)
        for u in online.gin_var:
            u.write_nowrap(line)

        self.clock.stop()
        self.is_active = False
        if result_code != '*':
            history.history.save_game(self, msg, result_code)
            if self.rated:
                if result_code == '1-0':
                    (white_score, black_score) = (1.0, 0.0)
                elif result_code == '1/2-1/2':
                    (white_score, black_score) = (0.5, 0.5)
                elif result_code == '0-1':
                    (white_score, black_score) = (0.0, 1.0)
                else:
                    raise RuntimeError('game.result: unexpected result code')
                rating.update_ratings(self, white_score, black_score)

        if self.bug_link and self.bug_link.is_active:
            if result_code == '1-0':
                self.bug_link.result("%s's partner won" %
                    self.white.session.partner.name, '0-1')
            elif result_code == '0-1':
                self.bug_link.result("%s's partner won" %
                    self.black.session.partner.name, '1-0')
            elif result_code == '1/2-1/2':
                self.bug_link.result("Partners' game drawn", '1/2-1/2')
            elif result_code == '*':
                if 'Game adjourned' in msg:
                    self.bug_link.adjourn("Partners' game adjourned")
                elif 'Game aborted' in msg:
                    self.bug_link.result("Partners' game aborted", '*')
                else:
                    print 'unexpected incomplete game message %s' % msg
                    assert(False)
            else:
                print 'unexpected result code %s' % result_code
                assert(False)

        self.free()

    def moretime(self, secs, u):
        """ Player "u" adds more time to the clock of his or her
        opponent. """
        assert(u in self.players)
        opp = self.get_opp(u)
        self.clock.moretime(self.get_user_side(opp), secs)
        u.write(_("You have added %(secs)d seconds to %(oname)s's clock.\n") %
            {'oname': opp.name, 'secs': secs})
        opp.write_("%(uname)s has added %(secs)d seconds to your clock.\n",
            {'uname': u.name, 'secs': secs})
        for p in self.observers:
            p.write_("%(uname)s has added %(secs)d seconds to %(oname)s's clock.\n",
                {'uname': u.name, 'secs': secs, 'oname': opp.name})
        self.send_boards()

    def allobservers(self, conn):
        if self.observers:
            olist = [u.get_display_name() for u in self.observers]
            conn.write(ngettext('Observing %d [%s vs. %s]: %s (%d user)\n',
                    'Observing %d [%s vs. %s]: %s (%d users)\n',
                    len(olist)) %
                (self.number, self.white_name, self.black_name,
                    ' '.join(olist), len(olist)))
            return True
        else:
            return False

    def resign(self, user):
        side = self.get_user_side(user)
        if side == WHITE:
            self.result('%s resigns' % user.name, '0-1')
        else:
            assert(side == BLACK)
            self.result('%s resigns' % user.name, '1-0')

    def leave(self, user):
        side = self.get_user_side(user)
        opp = self.get_opp(user)
        opp.write_('\nYour opponent has lost contact or quit.\n')
        if (user.is_guest or user.has_title('abuser') or
                (user.vars['noescape'] and opp.vars['noescape'])):
            res = '0-1' if side == WHITE else '1-0'
            self.result('%s forfeits by disconnection' % user.name, res)
        elif opp.is_guest or self.variant.pos.ply < 10:
            # registered player quits while playing a guest, or
            # game too short to adjourn: abort
            self.result('%s aborts by disconnection' % user.name, '*')
        else:
            # two registered players; adjourn game
            self.adjourn('%s lost connection; game adjourned' % user.name)

    def adjourn(self, reason):
        """ Adjourn this game by saving it to the database and notifying
        the players and observers. """
        data = self.tags.copy()
        data.update({
            'white_user_id': self.white.id,
            #'white_rating': int(self.white_rating),
            'white_clock': self.clock.get_white_time(),
            'black_user_id': self.black.id,
            #'black_rating': int(self.black_rating),
            'black_clock': self.clock.get_black_time(),
            'movetext': self.get_movetext(),
            'eco': self.get_eco()[1],
            'ply_count': self.get_ply_count(),
            'variant_id': self.speed_variant.variant.id_,
            'speed_id': self.speed_variant.speed.id_,
            'rated': self.rated,
            'when_started': self.when_started,
            'when_adjourned': datetime.datetime.utcnow()
        })
        if self.clock_name == 'overtime':
            data.update({
                'overtime_move_num': self.overtime_move_num,
                'overtime_bonus': self.overtime_bonus
            })
        if 'connect' in reason:
            data['adjourn_reason'] = 'Dis'
        elif 'by agreement' in reason:
            data['adjourn_reason'] = 'Agr'
        else:
            raise RuntimeError('unable to abbreviate adjournment reason: %s' %
                reason)
        db.adjourned_game_add(data)
        self.result(reason, '*')

    def free(self):
        super(PlayedGame, self).free()
        assert(self.white.session.game == self)
        assert(self.black.session.game == self)
        self.white.session.game = None
        self.black.session.game = None

    '''def __getitem__(self, key):
        """ Used to make game objects subscriptable, so they can
        be passed directly to MySQLdb methods """
        #assert(key in self._keys)
        return self.__dict__[key]'''

    #_keys = ['white_id', 'black_id', 'movetext']
    #def keys(self):
    #    return self._keys

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
