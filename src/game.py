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
from timer import timer
from db import db
from game_constants import *

games = {}

from variant.variant_factory import variant_factory

def opp(side):
    assert(side in [WHITE, BLACK])
    return BLACK if side == WHITE else WHITE

def side_to_str(side):
    assert(side in [WHITE, BLACK])
    return "white" if side == WHITE else "black"

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
        u = user.find.by_prefix_for_user(arg, conn,
            online_only=True)
        if u:
            if not u.session.games:
                conn.write(_("%s is not playing or examining a game.\n")
                    % u.name)
            else:
                g = u.session.games.current()
    return g

class Game(object):
    def __init__(self):
        self.number = find_free_slot()
        games[self.number] = self
        self.observers = set()
        self.pending_offers = []

    def send_boards(self):
        for p in self.players:
            p.send_board(self)
            if p.has_timeseal():
                p.session.ping(for_move=True)
        for u in self.observers:
            u.send_board(self)

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

    def get_user_opp_side(self, user):
        if user == self.white:
            return BLACK
        elif user == self.black:
            return WHITE
        else:
            raise RuntimeError('Game.get_opp_side(): got a non-player')

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

    def unobserve(self, u):
        """Remove the given user as an observer and notify the user."""
        u.write(_('Removing game %d from observation list.\n')
            % self.number)
        u.session.observed.remove(self)
        self.observers.remove(u)

    def free(self):
        for o in self.pending_offers:
            o.decline(notify=False)
        del games[self.number]
        for u in self.observers.copy():
            self.unobserve(u)
        assert(not self.observers)

    def get_eco(self):
        i = min(self.variant.pos.ply, 36)
        row = None
        while i >= self.variant.pos.start_ply:
            hash = self.variant.pos.history.get_hash(i)
            row = db.get_eco(hash)
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
            hash = self.variant.pos.history.get_hash(i)
            row = db.get_nic(hash)
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

        time_str = time.strftime("%a %b %e, %H:%M %Z %Y",
            time.localtime(self.start_time))

        # Original FICS prints (UNR) for unrated players here; in other
        # places it usually uses (++++) or (----) instead.  This looks like
        # gratuitous inconsistency to me, so let's see if we can get
        # away with using the same notation everywhere.
        if self.gtype == PLAYED:
            white_name = self.white.name
            black_name = self.black.name
            white_rating = self.white_rating
            black_rating = self.black_rating
            white_time = self.white_time
        else:
            assert(self.gtype == EXAMINED)
            white_name = self.players[0].name
            black_name = white_name
            white_rating = self.players[0].get_rating(self.speed_variant)
            black_rating = white_rating

        conn.write("%s (%s) vs. %s (%s) --- %s\n" % (white_name,
            white_rating, black_name, black_rating, time_str))

        conn.write("%s %s match, initial time: %d minutes, increment: %d seconds.\n\n" %
            (self.rated_str.capitalize(), self.speed_variant,
                self.white_time, self.inc))
        conn.write('Move  %-23s %s\n----  ---------------------   ---------------------\n' % (white_name, black_name))
        i = self.variant.pos.start_ply & ~1
        while i < self.variant.pos.ply:
            if i < self.variant.pos.start_ply:
                move_str = '...'
            else:
                mv = self.variant.pos.history.get_move(i)
                move_str = '%-7s (%s)' % (mv.to_san(), timer.hms(mv.time, conn.user))
            if i % 2 == 0:
                conn.write('%3d.  %-23s ' % (int((i + 3) / 2),move_str))
            else:
                assert(len(move_str) <= 23)
                conn.write('%s\n' % move_str)
            i += 1

        if i & 1 != 0:
            conn.write('\n')

        conn.write('      {Still in progress} *\n\n')

    def show_observers(self, conn):
        if self.observers:
            olist = [u.get_display_name() for u in self.observers]
            conn.write(ngettext('Observing %d [%s vs. %s]: %s (%d user)\n',
                    'Observing %d [%s vs. %s]: %s (%d users)\n',
                    len(olist)) %
                (self.number, self.white.name, self.black.name,
                ' '.join(olist), len(olist)))

    def parse_move(self, s, conn):
        try:
            mv = self.variant.parse_move(s, conn)
            parsed = mv is not None
            illegal = False
        except speed_variant.IllegalMoveError:
            illegal = True
            parsed = True
        if parsed:
            if self.gtype == PLAYED and (
                    self.get_user_side(conn.user) != self.variant.get_turn()):
                conn.write(_('It is not your move.\n'))
            elif illegal:
                conn.write(_('Illegal move (%s)\n') % s)
            else:
                self.variant.do_move(mv)
                self.next_move(mv, conn)
        return parsed

class PlayedGame(Game):
    def __init__(self, chal):
        super(PlayedGame, self).__init__()
        self.gtype = PLAYED

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
        self.players = [self.white, self.black]

        self.speed_variant = chal.speed_variant
        self.white_rating = self.white.get_rating(self.speed_variant)
        self.black_rating = self.black.get_rating(self.speed_variant)
        self.white_time = chal.time
        self.black_time = chal.time
        self.inc = chal.inc
        if chal.idn is not None:
            self.idn = chal.idn
        elif chal.idn == -1:
            # special value for "always random"
            self.idn = random.randint(0, 959)
        else:
            self.idn = self._pick_idn(chal.a, chal.b)
        if chal.clock_name == 'overtime':
            self.overtime_move_num = chal.overtime_move_num
            self.overtime_bonus = chal.overtime_bonus

        self.white.session.is_white = True
        self.black.session.is_white = False

        self.rated = chal.rated
        self.rated_str = 'rated' if self.rated else 'unrated'

        self.flip = False
        self.private = False
        self.start_time = time.time()
        self.is_active = True

        self.clock = clock.clock_names[chal.clock_name](self)
        self.when_started = datetime.datetime.utcnow()

        # Creating: GuestBEZD (0) admin (0) unrated blitz 2 12
        create_str = _('Creating: %s (%s) %s (%s) %s %s %d %d\n') % (self.white.name, self.white_rating, self.black.name, self.black_rating, self.rated_str, self.speed_variant, self.white_time, self.inc)

        self.white.write(create_str)
        self.black.write(create_str)

        create_str_2 = '\n{Game %d (%s vs. %s) Creating %s %s match.}\n' % (self.number, self.white.name, self.black.name, self.rated_str, self.speed_variant)
        self.white.write(create_str_2)
        self.black.write(create_str_2)

        if self.white.session.ivars['gameinfo'] or \
                self.black.session.ivars['gameinfo']:
            # The order of fields FICS sends differs from the
            # "help iv_gameinfo" documentation; the it= field gives
            # the initial time increment for white, and the i= field
            # does the same for black.  This seems wrong since "it" was
            # supposed to stand for "initial time", but compatability
            # with FICS is more important than being logical.
            gameinfo_str = '<g1> %d p=%d t=%s r=%d u=%d,%d it=%d,%d i=%d,%d pt=0 rt=%s,%s ts=%d,%d m=2 n=0\n' % (self.number, self.private, self.speed_variant.variant.name, self.rated, self.white.is_guest, self.black.is_guest, 60 * self.white_time, self.inc, 60 * self.black_time, self.inc, self.white_rating.ginfo_str(), self.black_rating.ginfo_str(), self.white.has_timeseal(), self.black.has_timeseal())
            if self.white.session.ivars['gameinfo']:
                self.white.write(gameinfo_str)
            if self.black.session.ivars['gameinfo']:
                self.black.write(gameinfo_str)

        self.variant = variant_factory.get(self.speed_variant.variant.name,
            self)

        self.white.session.games.add(self, self.black.name)
        self.black.session.games.add(self, self.white.name)

        self.white.session.last_opp = self.black
        self.black.session.last_opp = self.white

        self.send_boards()

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
                    elapsed = (conn.session.timeseal_last_timestamp -
                        conn.session.move_sent_timestamp) / 1000.0
                    time = self.clock.got_move(moved_side,
                        self.variant.pos.ply, elapsed)
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

        super(PlayedGame, self).next_move(mv, conn)

        if self.variant.pos.is_checkmate:
            if self.variant.get_turn() == WHITE:
                self.result('%s checkmated' % self.white.name, '0-1')
            else:
                self.result('%s checkmated' % self.black.name, '1-0')
        elif self.variant.pos.is_stalemate:
            self.result('Game drawn by stalemate', '1/2-1/2')
        elif self.variant.pos.is_draw_nomaterial:
            self.result('Game drawn because neither player has mating material', '1/2-1/2')

    def result(self, msg, result_code):
        self.when_ended = datetime.datetime.utcnow()
        line = '\n{Game %d (%s vs. %s) %s} %s\n' % (self.number,
            self.white.name, self.black.name, msg, result_code)
        self.white.write(line)
        self.black.write(line)
        for u in self.observers:
            u.write(line)

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
        self.free()

    def observe(self, u):
        u.session.observed.add(self)
        self.observers.add(u)
        u.write(_('You are now observing game %d.\n') % self.number)
        u.send_board(self)


    def resign(self, user):
        side = self.get_user_side(user)
        if side == WHITE:
            self.result('%s resigns' % user.name, '0-1')
        else:
            assert(side == BLACK)
            self.result('%s resigns' % user.name, '1-0')

    def leave(self, user):
        side = self.get_user_side(user)
        if user.is_guest: # or is an abuser
            res = '0-1' if side == WHITE else '1-0'
            self.result('%s forfeits by disconnection' % user.name, res)
        else:
            # TODO: store games between registered players
            self.result('%s aborts by disconnection' % user.name, '*')

    def free(self):
        super(PlayedGame, self).free()
        self.white.session.games.free(self.black.name)
        self.black.session.games.free(self.white.name)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
