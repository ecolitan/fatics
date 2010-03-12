import re

import speed
import command
import game
from game import WHITE, BLACK

class Offer(object):
    """represents an offer from one player to another"""
    def __init__(self, name):
        self.name = name

    def accept(self):
        """player b accepts"""
        a = self.player_a.user
        b = self.player_b.user

        a.session.offers_sent.remove(self)
        b.session.offers_received.remove(self)

        b.write(_("Accepting the %s from %s.\n") % (self.name, a.name))
        a.write(_("%s accepts your %s.\n") % (b.name, self.name))

    def decline(self, logout=False, notify=True):
        """player b declines"""
        a = self.player_a.user
        b = self.player_b.user
        if notify:
            b.write(_("Declining the %s from %s.\n") % (self.name, a.name))
        a.session.offers_sent.remove(self)
        if not logout:
            if notify:
                a.write(_("%s declines the %s.\n") % (b.name, self.name))
            b.session.offers_received.remove(self)

    def withdraw(self, logout=False):
        """player a withdraws the offer"""
        a = self.player_a.user
        b = self.player_b.user
        a.write(_("Withdrawing your %s to %s.\n") % (self.name, b.name))
        if not logout:
            b.write(_("%s withdraws the %s.\n") % (a.name, self.name))
            a.session.offers_sent.remove(self)
        b.session.offers_received.remove(self)

class Abort(Offer):
    def __init__(self, game, user):
        Offer.__init__(self, 'abort offer')

        self.by = user
        offers = [o for o in game.pending_offers if o.name == self.name]
        if len(offers) > 1:
            raise RuntimeError('more than one abort offer in game %d' \
                % game.number)
        if len(offers) > 0:
            o = offers[0]
            if o.by == self.by:
                user.write(N_('You are already offering to abort game %d.\n') % game.number)
            else:
                game.abort('Game aborted by agreement')
        else:
            # XXX should not substitute name till translation
            game.pending_offers.append(self)
            #side = g.get_user_side(conn.user)
            #g.get_side_user(game.opp(side)).write(N_('%s requests to abort the game; type "abort" to accept.\n') % conn.user.name)
            game.get_opp(user).write(N_('%s requests to abort game %d; type "abort" to accept.\n') % (user.name, game.number))

class MatchPlayer(object):
    def __init__(self, u):
        self.user = u
        self.side = None

class Challenge(Offer):
    """represents a match offer from one player to another"""
    def __init__(self, a, b, opts):
        """a is the player issuing the offer; b receives the request"""
        Offer.__init__(self, "match offer")
        self.is_time_odds = False

        self.player_a = MatchPlayer(a)
        self.player_b = MatchPlayer(b)

        self.variant_name = 'normal'

        self.player_a.time = self.player_b.time = a.vars['time']
        self.player_a.inc = self.player_b.inc = a.vars['inc']

        self.rated = None
        # the side requested by a, if any
        self.side = None

        if opts != None:
            self._parse_opts(opts)
     
        if self.rated == None:
            if a.is_guest or b.is_guest:
                a.write(N_('Setting match to unrated.\n'))
                self.rated = False
            else:
                # historically, this was set according to the rated var
                self.rated = True

        #a.write('%(aname) (%(arat))%(acol) %(bname) %(brat) %(rat) %(variant)')
        if self.side != None:
            side_str = " [%s]" % game.side_to_str(self.side)
        else:
            side_str = ''
        
        self.player_a.rating = a.get_rating(self.variant_name)
        self.player_b.rating = b.get_rating(self.variant_name)

        rated_str = "rated" if self.rated else "unrated"

        if not self.is_time_odds:
            time_str = "%d %d" % (self.player_a.time, self.player_a.inc)
        else:
            time_str = "%d %d %d %d" % (self.player_a.time, self.player_a.inc, self.player_b.time, self.player_b.inc)
        expected_duration = self.player_a.time + self.player_a.inc * float(2) / 3
        assert(expected_duration > 0)
        if self.is_time_odds:
            self.speed = speed.nonstandard
        elif expected_duration < 3.0:
            self.speed = speed.lightning
        elif expected_duration < 15.0:
            self.speed = speed.blitz
        elif expected_duration < 75.0:
            self.speed = speed.standard
        else:
            self.speed = speed.slow

        if self.variant_name == 'normal':
            # normal chess has no variant name, e.g. "blitz"
            self.variant_and_speed = self.speed
        else:
            self.variant_and_speed = '%s %s' % (self.variant_name,self.speed)

        # example: Guest (++++) [white] hans (----) unrated blitz 5 0.
        challenge_str = '%s (%s)%s %s (%s) %s %s %s' % (self.player_a.user.name, self.player_a.rating, side_str, self.player_b.user.name, self.player_b.rating, rated_str, self.variant_and_speed, time_str)


        #if self.board != None:
        #    challenge_str = 'Loaded from a board'

        o = next((o for o in a.session.offers_received if
            o.equivalent_to(self)), None)
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
            b.write(N_('%s declines the offer and proposes a counteroffer.\n') % a.name)
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
        if (self.player_a.user == other.player_a.user and
                self.player_b.user == other.player_b.user and
                self.player_a.time == other.player_a.time and
                self.player_b.time == other.player_b.time and
                self.player_a.inc == other.player_a.inc and
                self.player_b.inc == other.player_b.inc and
                self.side == other.side):
            return True
        return False

    def equivalent_to(self, other):
        if self.variant_name != other.variant_name:
            return False

        # opposite but equivalent?
        if (self.player_a.user == other.player_b.user and
                self.player_b.user == other.player_a.user and
                self.player_a.time == other.player_b.time and
                self.player_b.time == other.player_a.time and
                self.player_a.inc == other.player_b.inc and
                self.player_b.inc == other.player_a.inc and (
                (self.side == None and other.side == None) or
                (self.side in [WHITE, BLACK] and
                    other.side in [WHITE, BLACK] and
                    self.side != other.side))):
            return True

        return False
        
    def accept(self):
        Offer.accept(self)
        
        a = self.player_a.user
        b = self.player_b.user

        g = game.Game(self)
        a.session.games[b.name] = g
        b.session.games[a.name] = g

    def _set_rated(self, val):
        assert(val in [True, False])
        if self.rated != None:
            raise command.BadCommandError()
        self.rated = val
    
    def _set_side(self, val):
        assert(val in [WHITE, BLACK])
        if self.player_a.side != None:
            raise command.BadCommandError()
        self.player_a.side = val
        self.player_b.side = game.opp(val)
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
                    raise command.BadCommandError()
                times.append(num)
                continue

            if w in ['unrated', 'u']:
                self._set_rated(False)
            
            elif w in ['rated', 'r']:
                self._set_rated(False)

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

        if len(times) == 0:
            pass
        elif len(times) == 1:
            self.player_a.time = self.player_b.time = times[0]
            self.player_a.inc = self.player_b.inc = 0
        elif len(times) == 2:
            self.player_a.time = self.player_b.time = times[0]
            self.player_a.inc = self.player_b.inc = times[1]
        elif len(times) == 3:
            self.is_time_odds = True
            self.player_a.time = 60*times[0]
            self.player_a.inc = self.player_b.inc = times[1]
            self.player_b.time = 60*times[1]
        elif len(times) == 4:
            self.is_time_odds = True
            (self.player_a.time, self.player_a.inc,
                self.player_b.time, self.player_b.inc) = times
        else:
            assert(False)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
