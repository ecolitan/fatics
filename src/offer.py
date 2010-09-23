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

import re

import speed_variant
import command_parser
import game
import formula
import clock

from game_constants import *

shortcuts = {
    'r': 'rated',
    'u': 'unrated',
    'w': 'white',
    'b': 'black',
    'fischerrandom': 'chess960',
    'fischerandom': 'chess960',
    'fr': 'chess960',
    'cra': 'crazyhouse',
    'zh': 'crazyhouse',
}

class Offer(object):
    """represents an offer from one player to another"""
    def __init__(self, name):
        self.name = name

    def accept(self):
        """player b accepts"""
        self.a.session.offers_sent.remove(self)
        self.b.session.offers_received.remove(self)

        self.b.write(_("Accepting the %s from %s.\n") % (self.name,
            self.a.name))
        self.a.write(_("%s accepts your %s.\n") % (self.b.name,
            self.name))

    def decline(self, notify=True):
        """player b declines"""
        if notify:
            self.a.write(_("%s declines your %s.\n") % (self.b.name,
                self.name))
            self.b.write(_("Declining the %s from %s.\n") % (self.name,
                self.a.name))
        self.a.session.offers_sent.remove(self)
        self.b.session.offers_received.remove(self)

    def withdraw(self, notify=True):
        """player a withdraws the offer"""
        if notify:
            self.a.write(_("Withdrawing your %s to %s.\n") % (self.name,
                self.b.name))
            self.b.write(_("%s withdraws the %s.\n") % (self.a.name,
                self.name))
        self.a.session.offers_sent.remove(self)
        self.b.session.offers_received.remove(self)

class Abort(Offer):
    def __init__(self, game, user):
        Offer.__init__(self, 'abort offer')

        self.a = user
        self.b = game.get_opp(user)
        self.game = game
        offers = [o for o in game.pending_offers if o.name == self.name]
        if len(offers) > 1:
            raise RuntimeError('more than one abort offer in game %d' \
                % game.number)
        if len(offers) > 0:
            o = offers[0]
            if o.a == self.a:
                user.write_('You are already offering to abort game %d.\n', (game.number,))
            else:
                o.accept()
        else:
            game.pending_offers.append(self)
            user.write_('Requesting to abort game %d.\n', (game.number,))
            self.b.write_('%s requests to abort game %d.\n', (user.name, game.number))
            a_sent = user.session.offers_sent
            b_received = self.b.session.offers_received
            a_sent.append(self)
            b_received.append(self)

    def decline(self, notify=True):
        Offer.decline(self, notify)
        self.game.pending_offers.remove(self)

    def accept(self):
        Offer.accept(self)
        self.game.pending_offers.remove(self)
        self.game.result('Game aborted by agreement', '*')

    def withdraw(self, notify=True):
        Offer.withdraw(self, notify)
        self.game.pending_offers.remove(self)

class Draw(Offer):
    def __init__(self, game, user):
        Offer.__init__(self, 'draw offer')

        self.a = user
        self.b = game.get_opp(user)
        self.game = game
        offers = [o for o in game.pending_offers if o.name == self.name]
        if len(offers) > 1:
            raise RuntimeError('more than one draw offer in game %d' \
                % game.number)
        if len(offers) > 0:
            o = offers[0]
            if o.a == self.a:
                user.write_('You are already offering a draw.\n')
            else:
                o.accept()
        else:
            # check for draw by 50-move rule, repetition
            # The old fics checked for 50-move draw before repetition,
            # and we do the same so the adjudications are identical.
            if game.variant.pos.is_draw_fifty():
                game.result('Game drawn by the 50 move rule', '1/2-1/2')
                return
            elif game.variant.pos.is_draw_repetition(game.get_user_side(
                    self.a)):
                game.result('Game drawn by repetition', '1/2-1/2')
                return

            game.pending_offers.append(self)
            user.write_('Offering a draw to %s.\n', (self.b.name,))
            self.b.write_('%s offers a draw.\n', (user.name,))

            a_sent = user.session.offers_sent
            b_received = self.b.session.offers_received
            a_sent.append(self)
            b_received.append(self)

    def accept(self):
        Offer.accept(self)
        self.game.pending_offers.remove(self)
        self.game.result('Game drawn by agreement', '1/2-1/2')

    def decline(self, notify=True):
        Offer.decline(self, notify)
        self.game.pending_offers.remove(self)

    def withdraw(self, notify=True):
        if notify:
            self.a.write(_('You cannot withdraw a draw offer.\n'))

#class InvalidOfferError(Exception):
#    pass

class Challenge(Offer):
    """ represents a match offer from one player to another """
    def __init__(self, a, b, opts):
        """a is the player issuing the offer; b receives the request"""
        Offer.__init__(self, "match offer")

        self.a = a
        self.b = b

        self.variant_name = None
        self.clock_name = None

        self.time = None
        self.inc = None
        self.rated = None
        self.side = None # the side requested by a, if any
        self.idn = None

        if opts is not None:
            self._parse_opts(opts)

        if self.rated is None:
            if a.is_guest or b.is_guest or self.clock_name in [
                    'hourglass', 'untimed']:
                a.write_('Setting match offer to unrated.\n')
                self.rated = False
            else:
                # historically, this was set according to the rated var
                self.rated = True
        elif self.rated and (a.is_guest or b.is_guest):
            a.write_('Only registered players can play rated games.\n')
            #raise InvalidOfferError()
            return
        elif self.rated and self.clock_name in ['hourglass', 'untimed']:
            a.write_('This clock type cannot be used in rated games.\n')
            return

        if self.clock_name == 'untimed':
            if self.time != 0:
                self._set_time(0)
            if self.inc != 0:
                self._set_inc(0)

        if self.time is None:
            self.time = a.vars['time']
        if self.inc is None:
            if self.clock_name == 'hourglass':
                # default to no increment
                self.inc = 0
            else:
                self.inc = a.vars['inc']

        if self.clock_name == 'bronstein' and not self.inc:
            a.write_('Games using a Bronstein clock must have an increment.\n')
            return
        if self.clock_name == 'hourglass' and self.inc:
            a.write_('Games using an hourglass clock may not have an increment.\n')
            return
        if self.clock_name == 'overtime':
            if self.time < 1:
                a.write_('Games using an overtime clock must have a positive initial time.\n')
                return
            if self.overtime_bonus < 1:
                a.write_('Games using an overtime clock must have a positive overtime bonus.\n')
                return
            # I would make the limit higher, but the test depends on it
            # being low....
            if self.overtime_move_num < 3:
                a.write_('Invalid number of moves before overtime bonus.\n')
                return
        if self.time == 0 and self.inc == 0:
            if self.clock_name != 'untimed':
                self._set_clock_name('untimed')

        if self.side is not None:
            side_str = ' [%s]' % game.side_to_str(self.side)
        else:
            side_str = ''

        if self.variant_name is None:
            # chess is the default, of course
            self.variant_name = 'chess'

        if self.clock_name is None:
            self.clock_name = 'fischer'

        if self.idn is not None and self.variant_name != 'chess960':
            # idns can only be used for chess960
            a.write_('You may only specify an idn for chess960 games.\n')
            return

        rated_str = "rated" if self.rated else "unrated"

        if self.clock_name == 'untimed':
            self.speed_name = 'untimed'
        else:
            expected_duration = self.time + self.inc * float(2) / 3
            if self.clock_name == 'overtime':
                expected_duration += self.overtime_bonus
            elif self.clock_name == 'hourglass':
                # ???
                expected_duration *= 3
            assert(expected_duration > 0)
            if expected_duration < 3.0:
                self.speed_name = 'lightning'
            elif expected_duration < 15.0:
                self.speed_name = 'blitz'
            elif expected_duration < 75.0:
                self.speed_name = 'standard'
            else:
                self.speed_name = 'slow'

        self.speed_variant = speed_variant.from_names(self.speed_name,
            self.variant_name)
        self.a_rating = a.get_rating(self.speed_variant)
        self.b_rating = b.get_rating(self.speed_variant)

        if self.clock_name == 'untimed':
            time_str = ''
        else:
            time_str = ' %d %d' % (self.time, self.inc)


        # example: Guest (++++) [white] hans (----) unrated blitz 5 0.
        challenge_str = '%s (%s)%s %s (%s) %s %s%s' % (self.a.name, self.a_rating, side_str, self.b.name, self.b_rating, rated_str, self.speed_variant, time_str)

        if self.idn is not None:
            challenge_str = '%s idn=%d' % (challenge_str, self.idn)
        if self.clock_name not in ['fischer', 'untimed']:
            challenge_str = '%s %s' % (challenge_str, self.clock_name)
        if self.clock_name == 'overtime':
            challenge_str = '%s %d/%d,SD/%d+%d' % (challenge_str,
                self.overtime_move_num, self.time, self.overtime_bonus,
                self.inc)

        #if self.board is not None:
        #    challenge_str = 'Loaded from a board'

        o = next((o for o in a.session.offers_received if
            o.name == self.name and o.equivalent_to(self)), None)
        if o:
            # a already received an identical offer, so just accept it
            o.accept()
            return

        a_sent = a.session.offers_sent
        b_sent = b.session.offers_sent
        a_received = a.session.offers_received
        b_received = b.session.offers_received

        if self in a_sent:
            a.write_('You are already offering an identical match to %s.\n',
                (b.name,))
            return

        if not formula.check_formula(self, b.vars['formula']):
            a.write_('Match request does not meet formula for %s:\n', b.name)
            b.write_('Ignoring (formula): %s\n', challenge_str)
            return

        o = next((o for o in b_sent if o.name == self.name), None)
        if o:
            a.write_('Declining the offer from %s and proposing a counteroffer.\n', (b.name,))
            b.write_('%s declines your offer and proposes a counteroffer.\n', (a.name,))
            o.decline(notify=False)

        o = next((o for o in a_sent if o.name == self.name), None)
        if o:
            a.write_('Updating the offer already made to %s.\n', (b.name,))
            b.write_('%s updates the offer.\n', (a.name,))
            a_sent.remove(o)
            b_received.remove(o)

        a_sent.append(self)
        b_received.append(self)

        a.write('Issuing: %s\n' % challenge_str)
        b.write('Challenge: %s\n' % challenge_str)
        if a.has_title('abuser'):
            b.write_('--** %s is an abuser **--\n', (a.name,))
        if b.has_title('abuser'):
            a.write_('--** %s is an abuser **--\n', (b.name,))
        if a.has_title('computer'):
            b.write_('--** %s is a computer **--\n', (a.name,))
        if b.has_title('computer'):
            a.write_('--** %s is a computer **--\n', (b.name,))
        b.write_('You can "accept", "decline", or propose different parameters.\n')

    def __eq__(self, other):
        if (self.name == other.name and
                self.a == other.a and
                self.b == other.b and
                self.time == other.time and
                self.inc == other.inc and
                self.side == other.side):
            return True
        return False

    def __hash__(self, other):
        return hash((self.a, self.b, self.time, self.inc, self.side))

    def equivalent_to(self, other):
        if self.speed_variant.variant != other.speed_variant.variant:
            return False

        # opposite but equivalent?
        if (self.a == other.b and
                self.b == other.a and
                self.time == other.time and
                self.inc == other.inc and
                (self.side is None and other.side is None) or
                (self.side in [WHITE, BLACK] and
                    other.side in [WHITE, BLACK] and
                    self.side != other.side)):
            return True

        return False

    def accept(self):
        Offer.accept(self)

        g = game.PlayedGame(self)

    def _set_rated(self, val):
        assert(val in [True, False])
        if self.rated is not None:
            raise command_parser.BadCommandError()
        self.rated = val

    def _set_side(self, val):
        assert(val in [WHITE, BLACK])
        if self.side is not None:
            raise command_parser.BadCommandError()
        self.side = val

    def _set_variant_name(self, val):
        if self.variant_name is not None:
            # conflicting variants
            raise command_parser.BadCommandError()
        self.variant_name = val

    def _set_clock_name(self, val):
        if self.clock_name is not None:
            # conflicting clock types
            raise command_parser.BadCommandError()
        self.clock_name = val

    def _set_time(self, val):
        if self.time is not None:
            raise command_parser.BadCommandError()
        assert(val >= 0)
        self.time = val

    def _set_inc(self, val):
        if self.inc is not None:
            raise command_parser.BadCommandError()
        assert(val >= 0)
        self.inc = val

    _wild_re = re.compile(r'w(\d+)')
    _idn_re = re.compile(r'idn=(\d+)')
    _plus_re = re.compile(r'(\d+)\+(\d+)')
    # e.g. 40/90,sd/30+30
    _overtime_re = re.compile(r'(\d+)/(\d+),sd/(\d+)(?:\+(\d+))?', re.I)
    def _parse_opts(self, opts):
        opts = opts.lower()
        args = re.split(r'\s+', opts)
        if not args:
            return

        do_wild = False
        times = []
        for w in args:
            if w in shortcuts:
                w = shortcuts[w]
            if not do_wild:
                try:
                    times.append(int(w))
                    continue
                except ValueError:
                    pass

            if do_wild:
                self._set_variant_name(w)
                do_wild = False
                continue

            if w == 'unrated':
                self._set_rated(False)
            elif w == 'rated':
                self._set_rated(True)
            elif w == 'white':
                self._set_side(WHITE)
            elif w == 'black':
                self._set_side(BLACK)

            elif w in speed_variant.variant_names:
                self._set_variant_name(w)

            elif w in clock.clock_names:
                self._set_clock_name(w)

            elif w == 'wild':
                do_wild = True
            else:
                m = re.match(self._wild_re, w)
                if m:
                    self._set_variant_name(m.group(1))
                    continue

                m = re.match(self._idn_re, w)
                if m:
                    self.idn = int(m.group(1))
                    if self.idn < -1 or self.idn > 959:
                        raise command_parser.BadCommandError
                    continue

                m = re.match(self._plus_re, w)
                if m:
                    self._set_time(int(m.group(1)))
                    self._set_inc(int(m.group(2)))
                    continue

                m = re.match(self._overtime_re, w)
                if m:
                    self._set_clock_name('overtime')
                    # e.g. 40/90,sd/30+30
                    self.overtime_move_num = int(m.group(1))
                    self._set_time(int(m.group(2)))
                    self.overtime_bonus = int(int(m.group(3)))
                    if m.group(4) is not None:
                        self._set_inc(int(m.group(4)))
                    else:
                        self._set_inc(0)
                    continue

                #print('got unknown keyword %s' % w)
                raise command_parser.BadCommandError()



        if len(times) > 2:
            # time odds not supported
            raise command_parser.BadCommandError()
        elif len(times) == 2:
            self._set_time(times[0])
            self._set_inc(times[1])
        elif len(times) == 1:
            self._set_time(times[0])

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
