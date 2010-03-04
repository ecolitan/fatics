"""This implements routines for normal chess.  (I avoid the term
standard since that is used to describe the game speed on FICS.)
Maybe normal chess technically not a variant, but organizationally
I didn't want to privilege it over variants, so it is here. """

from variant import Variant

class Normal(Variant):
    def __init__(self, fen=None):
        print 'this is normal chess'

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
