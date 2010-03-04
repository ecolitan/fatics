import re

import variant
import speed
import command
import game
from game import WHITE, BLACK

class MatchPlayer(object):
    def __init__(self, u):
        self.user = u
        self.side = None


class Challenge(object):
    """represents a challenge from one player to another"""
    def __init__(self, a, b, opts):
        """a is the player issuing the challenge; b receives the request"""
        self.is_time_odds = False

        self.player_a = MatchPlayer(a)
        self.player_b = MatchPlayer(b)

        self.variant = variant.normal

        self.player_a.time = self.player_b.time = a.vars['time']
        self.player_a.inc = self.player_b.inc = a.vars['inc']

        self.rated = None
        self.side = None

        if opts != None:
            self._parse_opts(opts)
      
        if self.rated == None:
            # historically, this was set according to the rated var
            self.rated = True

        #a.write('%(aname) (%(arat))%(acol) %(bname) %(brat) %(rat) %(variant)')
        if self.player_a.side != None:
            side_str = " [%s]" % game.side_to_str(self.player[1])
        else:
            side_str = ''
        
        self.player_a.rating = a.get_rating(self.variant)
        self.player_b.rating = b.get_rating(self.variant)

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

        # example: admin (++++) [white] hans (----) unrated blitz 5 0.
        challenge_str = '%s (%s)%s %s (%s) %s %s %s' % (self.player_a.user.name, self.player_a.rating, side_str, self.player_b.user.name, self.player_b.rating, rated_str, self.speed, time_str)


        #if self.board != None:
        #    challenge_str = challenge_str = 'Loaded from a board'
        
        sent = a.session.pending_sent
        received = b.session.pending_received
        if b.name in sent:
            a.write(_('Updating offer already made to %s.\n') % b.name)
            del sent[b.name]
            del received[a.name]
        sent[b.name] = self
        received[a.name] = self

        a.write('Issuing: %s\n' % challenge_str)
        b.write('Challenge: %s\n' % challenge_str)
        b.write(_('You can "accept", "decline", or propose different parameters.\n'))
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
        self.variant = None

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

        if len(times) == 1:
            self.w_time = self.b_time = times[0]
            self.w_inc = self.b_inc = 0
        elif len(times) == 2:
            self.w_time = self.b_time = times[0]
            self.w_inc = self.b_inc = times[1]
        elif len(times) == 3:
            self.is_time_odds = True
            self.w_time = 60*times[0]
            self.w_inc = self.b_inc = times[1]
            self.b_time = 60*times[1]
        elif len(times) == 4:
            self.is_time_odds = True
            (self.w_time, self.w_inc, self.b_time, self.b_inc) = times
        else:
            assert(False)

    """player b accepts"""
    def accept(self):
        a = self.player_a.user
        b = self.player_b.user

        del a.session.pending_sent[b.name]
        del b.session.pending_received[a.name]

        b.write(_("You accept the challenge of %s.\n") % a.name)
        a.write(_("%s accepts your challenge.\n") % b.name)
        g = game.Game(self)
        a.session.games[b.name] = g
        b.session.games[a.name] = g

    """player b declines"""
    def decline(self): 
        a = self.player_a.user
        self.player_b.user.write(_("Declining the challenge from %s.\n") % a.name)
        del a.session.pending_sent[self.player_b.user.name]

    """player a withdraws the offer"""
    def withdraw(self): 
        b = self.player_b.user
        self.player_a.user.write(_("Withdrawing your challenge to %s.\n") % b.name)
        del b.session.pending_received[self.player_a.user.name]

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
