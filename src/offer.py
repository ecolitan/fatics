import re

import speed_variant
import command_parser
import game
from game import WHITE, BLACK

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
                user.write(N_('You are already offering to abort game %d.\n') % game.number)
            else:
                o.accept()
        else:
            # XXX should not substitute name till translation
            game.pending_offers.append(self)
            user.write(N_('Requesting to abort game %d.\n') % game.number)
            self.b.write(N_('%s requests to abort game %d.\n') % (user.name, game.number))
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
                user.write(N_('You are already offering a draw.\n'))
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
            user.write(N_('Offering a draw to %s.\n') % self.b.name)
            self.b.write(N_('%s offers a draw.\n') % user.name)

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
    """represents a match offer from one player to another"""
    def __init__(self, a, b, opts):
        """a is the player issuing the offer; b receives the request"""
        Offer.__init__(self, "match offer")

        self.a = a
        self.b = b

        self.variant_name = 'chess'

        self.time = a.vars['time']
        self.inc = a.vars['inc']

        self.rated = None
        # the side requested by a, if any
        self.side = None

        if opts is not None:
            self._parse_opts(opts)

        if self.rated is None:
            if a.is_guest or b.is_guest:
                a.write(N_('Setting match offer to unrated.\n'))
                self.rated = False
            else:
                # historically, this was set according to the rated var
                self.rated = True
        elif self.rated and (a.is_guest or b.is_guest):
            a.write(_('Only registered users can play rated games.\n'))
            #raise InvalidOfferError()
            return

        #a.write('%(aname) (%(arat))%(acol) %(bname) %(brat) %(rat) %(variant)')
        if self.side is not None:
            side_str = " [%s]" % game.side_to_str(self.side)
        else:
            side_str = ''

        rated_str = "rated" if self.rated else "unrated"

        time_str = "%d %d" % (self.time, self.inc)
        expected_duration = self.time + self.inc * float(2) / 3
        assert(expected_duration > 0)
        if expected_duration < 3.0:
            speed_name = 'lightning'
        elif expected_duration < 15.0:
            speed_name = 'blitz'
        elif expected_duration < 75.0:
            speed_name = 'standard'
        else:
            speed_name = 'slow'

        self.speed_variant = speed_variant.from_names(speed_name,
            self.variant_name)
        self.a_rating = a.get_rating(self.speed_variant)
        self.b_rating = b.get_rating(self.speed_variant)


        # example: Guest (++++) [white] hans (----) unrated blitz 5 0.
        challenge_str = '%s (%s)%s %s (%s) %s %s %s' % (self.a.name, self.a_rating, side_str, self.b.name, self.b_rating, rated_str, self.speed_variant, time_str)


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
            a.write(N_('You are already offering an identical match to %s.\n') % b.name)
            return

        o = next((o for o in b_sent if o.name == self.name), None)
        if o:
            a.write(N_('Declining the offer from %s and proposing a counteroffer.\n') % b.name)
            b.write(N_('%s declines your offer and proposes a counteroffer.\n') % a.name)
            o.decline(notify=False)

        o = next((o for o in a_sent if o.name == self.name), None)
        if o:
            a.write(N_('Updating the offer already made to %s.\n') % b.name)
            b.write(N_('%s updates the offer.\n') % a.name)
            a_sent.remove(o)
            b_received.remove(o)

        a_sent.append(self)
        b_received.append(self)

        a.write('Issuing: %s\n' % challenge_str)
        b.write('Challenge: %s\n' % challenge_str)
        b.write(N_('You can "accept", "decline", or propose different parameters.\n'))

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

    def _set_wild(self, val):
        self.variant_name = val

    def _parse_opts(self, opts):
        args = re.split(r'\s+', opts)
        times = []
        do_wild = False
        for w in args:
            try:
                num = int(w, 10)
            except ValueError:
                pass
            else:
                if do_wild:
                    do_wild = False
                    self._set_wild(w)
                if len(times) > 3:
                    # no more than 4 time values should be given
                    raise command_parser.BadCommandError()
                times.append(num)
                continue

            if w in ['unrated', 'u']:
                self._set_rated(False)

            elif w in ['rated', 'r']:
                self._set_rated(True)

            elif w in ['white', 'w']:
                self._set_side(WHITE)

            elif w in ['black', 'b']:
                self._set_side(BLACK)

            else:
                m = re.match('w(\d+)', w)
                if m:
                    self._set_wild(m.group(1))
                elif w == 'wild':
                    do_wild = True
                else:
                    raise command_parser.BadCommandError()

        if len(times) == 0:
            pass
        elif len(times) == 1:
            self.time = times[0]
            self.inc = 0
        elif len(times) == 2:
            self.time = times[0]
            self.inc = times[1]
        else:
            raise RuntimeError('internal error parsing match times')

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
