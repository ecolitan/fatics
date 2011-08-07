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

from test import *

import speed_variant

class TestGinfo(Test):
    def test_ginfo_played(self):
        t = self.connect_as_guest('GuestABCD')
        t2 = self.connect_as_guest('GuestEFGH')
        t3 = self.connect_as_guest()

        t.write('match guestefgh white 4+14\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('Creating: ', t)

        t3.write('iset ms 1\n')
        self.expect('ms set', t3)

        t.write('Nf3\n')
        self.expect('Nf3', t2)

        t3.write('ginfo guestabcd\n')
        self.expect('Game 1: Game information.', t3)
        self.expect('  GuestABCD (++++) vs GuestEFGH (++++) unrated blitz game.', t3)
        self.expect('  Time controls: 240 14', t3)
        self.expect('  Time of starting:', t3)
        self.expect('   White time 4:00.000    Black time 4:00.000', t3)
        self.expect('  The clock is not paused', t3)
        self.expect('  1 halfmove has been made.', t3)
        self.expect('  Fifty move count started at halfmove 0 (99 halfmoves until a draw).', t3)
        self.expect('  White may castle both kingside and queenside.', t3)
        self.expect('  Black may castle both kingside and queenside.', t3)
        self.expect("  Double pawn push didn't occur.", t3)
        t.write('abo\n')

        self.close(t)
        self.close(t2)
        self.close(t3)

    def test_ginfo_ep(self):
        t = self.connect_as_guest('GuestABCD')
        t2 = self.connect_as_guest('GuestEFGH')

        t.write('set style 12\n')
        t2.write('set style 12\n')

        t.write('match guestefgh white 5+15\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('Creating: ', t)

        moves = ['e4', 'e6', 'e5', 'd5']
        wtm = True
        for mv in moves:
            if wtm:
                t.write('%s\n' % mv)
            else:
                t2.write('%s\n' % mv)
            self.expect('<12> ', t)
            self.expect('<12> ', t2)
            wtm = not wtm

        t.write('ginfo\n')
        self.expect('Game 1: Game information.', t)
        self.expect('  GuestABCD (++++) vs GuestEFGH (++++) unrated standard game.', t)
        self.expect('  Time controls: 300 15', t)
        self.expect('  Time of starting: ', t)
        self.expect_re(r'   White time \d+:\d+    Black time \d+:\d+', t)
        self.expect('  The clock is not paused', t)
        self.expect('  4 halfmoves have been made.', t)
        self.expect('  Fifty move count started at halfmove 4 (100 halfmoves until a draw).', t)
        self.expect('  White may castle both kingside and queenside.', t)
        self.expect('  Black may castle both kingside and queenside.', t)
        self.expect('  Double pawn push occurred on the d-file.', t)
        t.write('abo\n')
        t2.write('abo\n')

        self.close(t)
        self.close(t2)

    def test_ginfo_examined(self):
        t = self.connect_as_guest('GuestABCD')

        t.write('ex\n')
        self.expect('Starting a game', t)
        for mv in ['e4', 'e5', 'Ke2']:
            t.write('%s\n' % mv)
        t.write('ginfo guestabcd\n')

        self.expect('Game 1: Game information.', t)

        self.expect('  GuestABCD is examining GuestABCD vs GuestABCD.', t)
        self.expect('  3 halfmoves have been made.', t)
        self.expect('  Fifty move count started at halfmove 2 (99 halfmoves until a draw).', t)
        self.expect('  White may not castle.', t)
        self.expect('  Black may castle both kingside and queenside.', t)
        self.expect("  Double pawn push didn't occur.", t)

        self.close(t)

    def test_ginfo_variant(self):
        t = self.connect_as_guest('GuestABCD')
        t2 = self.connect_as_guest('GuestEFGH')

        for vname in speed_variant.variant_names:
            if vname in ['chess', 'bughouse']: # XXX test bughouse
                continue
            t.write('match guestefgh white %s 3+0\n' % vname)
            self.expect('Challenge:', t2)
            t2.write('accept\n')
            self.expect('Creating: ', t)

            t2.write('ginfo\n')
            self.expect('Game 1: Game information.', t2)
            if vname != 'chess':
                self.expect('unrated blitz %s' % vname, t2)
            t.write('abo\n')
            self.expect('aborted on move 1', t2)

        self.close(t)
        self.close(t2)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
