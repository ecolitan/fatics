import re

import speed
import command
import game
from game import WHITE, BLACK

class Offer(object):
    pass

class MatchPlayer(object):
    def __init__(self, u):
        self.user = u
        self.side = None

class Challenge(Offer):
    """represents a match offer from one player to another"""
    def __init__(self, a, b, opts):
        """a is the player issuing the offer; b receives the request"""
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
        #    challenge_str = challenge_str = 'Loaded from a board'
        
        sent = a.session.pending_sent
        received = b.session.pending_received
        if b.name in sent:
            a.write(_('Updating the offer already made to %s.\n') % b.name)
            del sent[b.name]
            del received[a.name]
        sent[b.name] = self
        received[a.name] = self

        a.write('Issuing: %s\n' % challenge_str)
        b.write('Challenge: %s\n' % challenge_str)
        b.write(N_('You can "accept", "decline", or propose different parameters.\n'))
    def set_rated(self, val):
        assert(val in [True, False])
        if self.rated != None:
            raise command.BadCommandError()
        self.rated = val
    
    def set_side(self, val):
        assert(val in [WHITE, BLACK])
        if self.player_a.side != None:
            raise command.BadCommandError()
        self.player_a.side = val
        self.player_b.side = game.opp(val)
        self.side = val
    
    def set_wild(self, val):
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
                    self.set_wild(w)
                if len(times) > 3:
                    # no more than 4 time values should be given
                    raise command.BadCommandError()
                times.append(num)
                continue

            if w in ['unrated', 'u']:
                self.set_rated(False)
            
            elif w in ['rated', 'r']:
                self.set_rated(False)

            elif w in ['white', 'w']:
                self.set_side(WHITE)
            
            elif w in ['black', 'b']:
                self.set_side(BLACK)
         
            else:
                m = re.match('w(\d+)', w)
                if m:
                    self.set_wild(m.group(1))
                elif w == 'wild':
                    do_wild = True

        if len(times) == 0:
            pass
        elif len(times) == 1:
            self.player_a.time = self.player_b.time = times[0]
            self.player_a.inc = self.player_b.inc = 0
        elif len(times) == 2:
            self.player_a.time = self.player_b.time = times[0]
            self.player_a.inc = self.player_b_inc = times[1]
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

    """player b accepts"""
    def accept(self):
        a = self.player_a.user
        b = self.player_b.user

        del a.session.pending_sent[b.name]
        del b.session.pending_received[a.name]

        b.write(_("Accepting the offer from %s.\n") % a.name)
        a.write(_("%s accepts your offer.\n") % b.name)
        g = game.Game(self)
        a.session.games[b.name] = g
        b.session.games[a.name] = g

    """player b declines"""
    def decline(self, logout=False):
        a = self.player_a.user
        b = self.player_b.user
        b.write(_("Declining the offer from %s.\n") % a.name)
        del a.session.pending_sent[self.player_b.user.name]
        if not logout:
            a.write(_("%s declines the offer.\n") % b.name)
            del b.session.pending_received[self.player_a.user.name]

    """player a withdraws the offer"""
    def withdraw(self, logout=False):
        a = self.player_a.user
        b = self.player_b.user
        a.write(_("Withdrawing your offer to %s.\n") % b.name)
        if not logout:
            b.write(_("%s withdraws the offer.\n") % a.name)
            del a.session.pending_sent[self.player_b.user.name]
        del b.session.pending_received[self.player_a.user.name]

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
