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

from test.test import *
from bpgn import Bpgn

class TestBughouseMatch(Test):
    def test_match(self):
        t = self.connect_as_guest('GuestABCD')
        t2 = self.connect_as_guest('GuestEFGH')
        t3 = self.connect_as_guest('GuestIJKL')
        t4 = self.connect_as_guest('GuestMNOP')

        self.set_nowrap(t)
        self.set_nowrap(t2)
        self.set_nowrap(t3)
        self.set_nowrap(t4)

        t.write('match guestijkl bughouse\n')
        self.expect('You have no partner for bughouse.', t)

        t2.write('set bugopen\n')
        self.expect('You are now open for bughouse.', t2)
        t.write('part guestefgh\n')
        self.expect('GuestABCD offers', t2)
        t2.write('part guestabcd\n')
        self.expect('GuestEFGH accepts', t)

        t.write('match guestijkl bughouse\n')
        self.expect('Your opponent has no partner for bughouse.', t)

        t4.write('set bugopen\n')
        self.expect('You are now open for bughouse.', t4)
        t3.write('part guestmnop\n')
        self.expect('GuestIJKL offers', t4)
        t4.write('a\n')
        self.expect('GuestMNOP accepts', t3)

        t2.write('set open\n')
        self.expect('You are no longer open to receive match requests.', t2)
        t.write('match guestijkl bughouse 3+0\n')
        self.expect('Your partner is not available to play right now.', t)
        t2.write('set open\n')
        self.expect('You are now open to receive match requests.', t2)

        t4.write('ex\n')
        self.expect('Starting a game in examine (scratch) mode', t4)
        t.write('match guestijkl bughouse 3+0\n')
        self.expect("Your opponent's partner is not available to play right now.", t)
        t4.write('unex\n')
        self.expect('You are no longer examining', t4)

        t.write('match guestefgh bughouse 3+0\n')
        self.expect('You cannot challenge your own partner for bughouse.', t)

        t.write('match guestijkl bughouse 3+0\n')
        self.expect('Issuing: GuestABCD (++++) GuestIJKL (++++) unrated blitz bughouse 3 0', t)
        self.expect('Your bughouse partner issues: GuestABCD (++++) GuestIJKL (++++) unrated blitz bughouse 3 0', t2)
        self.expect('Your game will be: GuestEFGH (++++) GuestMNOP (++++) unrated blitz bughouse 3 0', t2)
        self.expect('Challenge: GuestABCD (++++) GuestIJKL (++++) unrated blitz bughouse 3 0', t3)
        self.expect('Your bughouse partner was challenged: GuestABCD (++++) GuestIJKL (++++) unrated blitz bughouse 3 0', t4)
        self.expect('Your game will be: GuestEFGH (++++) GuestMNOP (++++) unrated blitz bughouse 3 0', t4)

        self.close(t)
        self.close(t2)
        self.close(t3)
        self.close(t4)

    def test_match_partner_decline_by_playing(self):
        t = self.connect_as_guest('GuestABCD')
        t2 = self.connect_as_guest('GuestEFGH')
        t3 = self.connect_as_guest('GuestIJKL')
        t4 = self.connect_as_guest('GuestMNOP')

        self.set_nowrap(t)
        self.set_nowrap(t2)
        self.set_nowrap(t3)
        self.set_nowrap(t4)

        t2.write('set bugopen\n')
        self.expect('You are now open for bughouse.', t2)
        t.write('part guestefgh\n')
        self.expect('GuestABCD offers', t2)
        t2.write('part guestabcd\n')
        self.expect('GuestEFGH accepts', t)

        t4.write('set bugopen\n')
        self.expect('You are now open for bughouse.', t4)
        t3.write('part guestmnop\n')
        self.expect('GuestIJKL offers', t4)
        t4.write('a\n')
        self.expect('GuestMNOP accepts', t3)

        t.write('match guestijkl bughouse 3+0\n')
        self.expect('Issuing: GuestABCD (++++) GuestIJKL (++++) unrated blitz bughouse 3 0', t)

        t5 = self.connect_as_admin()
        t5.write('match guestmnop 1+0\n')
        self.expect('Challenge: admin', t4)
        t4.write('a\n')
        self.expect("GuestMNOP, whose partner you were challenging, has joined a game with admin.", t)
        self.expect("Challenge to GuestIJKL withdrawn.", t)
        self.expect("GuestMNOP, whose partner your partner was challenging, has joined a game with admin.", t2)
        self.expect("Partner's challenge to GuestIJKL withdrawn.", t2)
        self.expect("Your partner has joined a game with admin.", t3)
        self.expect("Challenge from GuestABCD removed.", t3)
        self.expect("Partner's challenge from GuestABCD removed.", t4)
        t5.write('abort\n')
        self.expect('aborted on move 1', t4)
        self.close(t5)

        self.close(t)
        self.close(t2)
        self.close(t3)
        self.close(t4)

    def test_match_decline_by_examining(self):
        t = self.connect_as_guest('GuestABCD')
        t2 = self.connect_as_guest('GuestEFGH')
        t3 = self.connect_as_guest('GuestIJKL')
        t4 = self.connect_as_guest('GuestMNOP')

        self.set_nowrap(t)
        self.set_nowrap(t2)
        self.set_nowrap(t3)
        self.set_nowrap(t4)

        t2.write('set bugopen\n')
        self.expect('You are now open for bughouse.', t2)
        t.write('part guestefgh\n')
        self.expect('GuestABCD offers', t2)
        t2.write('part guestabcd\n')
        self.expect('GuestEFGH accepts', t)

        t4.write('set bugopen\n')
        self.expect('You are now open for bughouse.', t4)
        t3.write('part guestmnop\n')
        self.expect('GuestIJKL offers', t4)
        t4.write('a\n')
        self.expect('GuestMNOP accepts', t3)

        t.write('match guestijkl bughouse 3+0\n')
        self.expect('Issuing: GuestABCD (++++) GuestIJKL (++++) unrated blitz bughouse 3 0', t)

        t3.write('ex\n')
        self.expect('Starting a game in examine (scratch) mode', t3)

        self.expect("GuestIJKL, whom you were challenging, has started examining a game.", t)
        self.expect("Challenge to GuestIJKL withdrawn.", t)
        self.expect("GuestIJKL, whom your partner was challenging, has started examining a game.", t2)
        self.expect("Partner's challenge to GuestIJKL withdrawn.", t2)
        self.expect('Challenge from GuestABCD removed.', t3)
        self.expect("Your partner has started examining a game.", t4)
        self.expect("Partner's challenge from GuestABCD removed.", t4)

        t4.write('unex\n')

        self.close(t)
        self.close(t2)
        self.close(t3)
        self.close(t4)

    def test_match_partner_withdraw_by_playing(self):
        t = self.connect_as_guest('GuestABCD')
        t2 = self.connect_as_guest('GuestEFGH')
        t3 = self.connect_as_guest('GuestIJKL')
        t4 = self.connect_as_guest('GuestMNOP')

        self.set_nowrap(t)
        self.set_nowrap(t2)
        self.set_nowrap(t3)
        self.set_nowrap(t4)

        t2.write('set bugopen\n')
        self.expect('You are now open for bughouse.', t2)
        t.write('part guestefgh\n')
        self.expect('GuestABCD offers', t2)
        t2.write('part guestabcd\n')
        self.expect('GuestEFGH accepts', t)

        t4.write('set bugopen\n')
        self.expect('You are now open for bughouse.', t4)
        t3.write('part guestmnop\n')
        self.expect('GuestIJKL offers', t4)
        t4.write('a\n')
        self.expect('GuestMNOP accepts', t3)

        t.write('match guestijkl bughouse 3+0\n')
        self.expect('Issuing: GuestABCD (++++) GuestIJKL (++++) unrated blitz bughouse 3 0', t)

        t5 = self.connect_as_admin()
        t5.write('match guestefgh 1+0\n')
        self.expect('Challenge: admin', t2)
        t2.write('a\n')

        self.expect("Your partner has joined a game with admin.", t)
        self.expect("Challenge to GuestIJKL withdrawn.", t)
        self.expect("Partner's challenge to GuestIJKL withdrawn.", t2)
        self.expect("GuestEFGH, whose partner was challenging you, has joined a game with admin.", t3)
        self.expect("Challenge from GuestABCD removed.", t3)
        self.expect("GuestEFGH, whose partner was challenging your partner, has joined a game with admin.", t4)
        self.expect("Partner's challenge from GuestABCD removed.", t4)

        t5.write('abort\n')
        self.expect('aborted on move 1', t2)
        self.close(t5)

        self.close(t)
        self.close(t2)
        self.close(t3)
        self.close(t4)

    def test_match_withdraw_by_playing(self):
        t = self.connect_as_guest('GuestABCD')
        t2 = self.connect_as_guest('GuestEFGH')
        t3 = self.connect_as_guest('GuestIJKL')
        t4 = self.connect_as_guest('GuestMNOP')

        t2.write('set bugopen\n')
        self.expect('You are now open for bughouse.', t2)
        t.write('part guestefgh\n')
        self.expect('GuestABCD offers', t2)
        t2.write('part guestabcd\n')
        self.expect('GuestEFGH accepts', t)

        t4.write('set bugopen\n')
        self.expect('You are now open for bughouse.', t4)
        t3.write('part guestmnop\n')
        self.expect('GuestIJKL offers', t4)
        t4.write('a\n')
        self.expect('GuestMNOP accepts', t3)

        t.write('match guestijkl bughouse 3+0\n')
        self.expect('Issuing: GuestABCD (++++) GuestIJKL (++++) unrated blitz bughouse 3 0', t)

        t5 = self.connect_as_admin()
        t5.write('match guestabcd 1+0\n')
        self.expect('Challenge: admin', t)
        t.write('a\n')

        self.expect("Challenge to GuestIJKL withdrawn.", t)
        self.expect("Your partner has joined a game with admin.", t2)
        self.expect("Partner's challenge to GuestIJKL withdrawn.", t2)
        self.expect("GuestABCD, who was challenging you, has joined a game with admin.", t3)
        self.expect("Challenge from GuestABCD removed.", t3)
        self.expect("GuestABCD, who was challenging your partner, has joined a game with admin.", t4)
        self.expect("Partner's challenge from GuestABCD removed.", t4)

        t5.write('abort\n')
        self.expect('aborted on move 1', t)
        self.close(t5)

        self.close(t)
        self.close(t2)
        self.close(t3)
        self.close(t4)


class TestBughouseKibitz(Test):
    def test_kibitz(self):
        # kibitz goes to all 4 players
        t = self.connect_as_guest('GuestABCD')
        t2 = self.connect_as_guest('GuestEFGH')
        t3 = self.connect_as_guest('GuestIJKL')
        t4 = self.connect_as_guest('GuestMNOP')

        self.set_nowrap(t)
        self.set_nowrap(t2)
        self.set_nowrap(t3)
        self.set_nowrap(t4)

        t2.write('set bugopen\n')
        self.expect('You are now open for bughouse.', t2)
        t.write('part guestefgh\n')
        self.expect('GuestABCD offers', t2)
        t2.write('part guestabcd\n')
        self.expect('GuestEFGH accepts', t)

        t4.write('set bugopen\n')
        self.expect('You are now open for bughouse.', t4)
        t3.write('part guestmnop\n')
        self.expect('GuestIJKL offers', t4)
        t4.write('a\n')
        self.expect('GuestMNOP accepts', t3)

        t.write('match guestijkl bughouse 3+0\n')
        self.expect('Issuing: GuestABCD (++++) GuestIJKL (++++) unrated blitz bughouse 3 0', t)
        self.expect('Your bughouse partner issues: GuestABCD (++++) GuestIJKL (++++) unrated blitz bughouse 3 0', t2)
        self.expect('Your game will be: GuestEFGH (++++) GuestMNOP (++++) unrated blitz bughouse 3 0', t2)
        self.expect('Challenge: GuestABCD (++++) GuestIJKL (++++) unrated blitz bughouse 3 0', t3)
        self.expect('Your bughouse partner was challenged: GuestABCD (++++) GuestIJKL (++++) unrated blitz bughouse 3 0', t4)
        self.expect('Your game will be: GuestEFGH (++++) GuestMNOP (++++) unrated blitz bughouse 3 0', t4)

        t3.write('match guestabcd bughouse 3+0\n') # intercept
        self.expect('Creating:', t)
        self.expect('Creating:', t2)
        self.expect('Creating:', t3)
        self.expect('Creating:', t4)

        t5 = self.connect_as_guest()
        t5.write('o guestmnop\n')
        self.expect('You are now observing', t5)

        t.write('ki this is a test\n')
        self.expect('GuestABCD(U)(++++)[1] kibitzes: this is a test', t)
        self.expect('GuestABCD(U)(++++)[1] kibitzes: this is a test', t2)
        self.expect('GuestABCD(U)(++++)[1] kibitzes: this is a test', t3)
        self.expect('GuestABCD(U)(++++)[1] kibitzes: this is a test', t4)
        self.expect('GuestABCD(U)(++++)[1] kibitzes: this is a test', t5)
        self.expect('(kibitzed to 4 players)', t)

        self.close(t5)

        self.close(t)
        self.close(t2)
        self.close(t3)
        self.close(t4)

    def test_whisper(self):
        # whisper goes to all 4 players
        t = self.connect_as_guest('GuestABCD')
        t2 = self.connect_as_guest('GuestEFGH')
        t3 = self.connect_as_guest('GuestIJKL')
        t4 = self.connect_as_guest('GuestMNOP')

        self.set_nowrap(t)
        self.set_nowrap(t2)
        self.set_nowrap(t3)
        self.set_nowrap(t4)

        t2.write('set bugopen\n')
        self.expect('You are now open for bughouse.', t2)
        t.write('part guestefgh\n')
        self.expect('GuestABCD offers', t2)
        t2.write('part guestabcd\n')
        self.expect('GuestEFGH accepts', t)

        t4.write('set bugopen\n')
        self.expect('You are now open for bughouse.', t4)
        t3.write('part guestmnop\n')
        self.expect('GuestIJKL offers', t4)
        t4.write('a\n')
        self.expect('GuestMNOP accepts', t3)

        t.write('match guestijkl bughouse 3+0\n')
        self.expect('Issuing: GuestABCD (++++) GuestIJKL (++++) unrated blitz bughouse 3 0', t)
        self.expect('Your bughouse partner issues: GuestABCD (++++) GuestIJKL (++++) unrated blitz bughouse 3 0', t2)
        self.expect('Your game will be: GuestEFGH (++++) GuestMNOP (++++) unrated blitz bughouse 3 0', t2)
        self.expect('Challenge: GuestABCD (++++) GuestIJKL (++++) unrated blitz bughouse 3 0', t3)
        self.expect('Your bughouse partner was challenged: GuestABCD (++++) GuestIJKL (++++) unrated blitz bughouse 3 0', t4)
        self.expect('Your game will be: GuestEFGH (++++) GuestMNOP (++++) unrated blitz bughouse 3 0', t4)

        t3.write('match guestabcd bughouse 3+0\n') # intercept
        self.expect('Creating:', t)
        self.expect('Creating:', t2)
        self.expect('Creating:', t3)
        self.expect('Creating:', t4)

        t5 = self.connect_as_guest()
        t5.write('o guestabcd\n')
        self.expect('You are now observing', t5)

        t3.write('whi this is a test\n')
        self.expect('GuestIJKL(U)(++++)[1] whispers: this is a test', t5)
        self.expect('(whispered to 1 player)', t3)

        self.close(t5)

        self.close(t)
        self.close(t2)
        self.close(t3)
        self.close(t4)

    def test_win_white(self):
        t = self.connect_as_guest('GuestABCD')
        t2 = self.connect_as_guest('GuestEFGH')
        t3 = self.connect_as_guest('GuestIJKL')
        t4 = self.connect_as_guest('GuestMNOP')

        self.set_nowrap(t)
        self.set_nowrap(t2)
        self.set_nowrap(t3)
        self.set_nowrap(t4)

        t2.write('set bugopen\n')
        self.expect('You are now open for bughouse.', t2)
        t.write('part guestefgh\n')
        self.expect('GuestABCD offers', t2)
        t2.write('part guestabcd\n')
        self.expect('GuestEFGH accepts', t)

        t4.write('set bugopen\n')
        self.expect('You are now open for bughouse.', t4)
        t3.write('part guestmnop\n')
        self.expect('GuestIJKL offers', t4)
        t4.write('a\n')
        self.expect('GuestMNOP accepts', t3)

        t.write('match guestijkl bughouse 3+0 w\n')
        self.expect('Issuing: GuestABCD (++++) [white] GuestIJKL (++++) unrated blitz bughouse 3 0', t)
        self.expect('Your bughouse partner issues: GuestABCD (++++) [white] GuestIJKL (++++) unrated blitz bughouse 3 0', t2)
        self.expect('Your game will be: GuestEFGH (++++) GuestMNOP (++++) unrated blitz bughouse 3 0', t2)
        self.expect('Challenge: GuestABCD (++++) [white] GuestIJKL (++++) unrated blitz bughouse 3 0', t3)
        self.expect('Your bughouse partner was challenged: GuestABCD (++++) [white] GuestIJKL (++++) unrated blitz bughouse 3 0', t4)
        self.expect('Your game will be: GuestEFGH (++++) GuestMNOP (++++) unrated blitz bughouse 3 0', t4)

        t3.write('a\n')
        self.expect('Creating:', t)
        self.expect('Creating:', t2)
        self.expect('Creating:', t3)
        self.expect('Creating:', t4)

        t2.write('res\n')
        self.expect('GuestEFGH resigns} 1-0', t2)
        self.expect('GuestEFGH resigns} 1-0', t4)
        self.expect("GuestIJKL's partner won} 0-1", t)
        self.expect("GuestIJKL's partner won} 0-1", t3)

        self.close(t)
        self.close(t2)
        self.close(t3)
        self.close(t4)

    def test_win_black(self):
        t = self.connect_as_guest('GuestABCD')
        t2 = self.connect_as_guest('GuestEFGH')
        t3 = self.connect_as_guest('GuestIJKL')
        t4 = self.connect_as_guest('GuestMNOP')

        self.set_nowrap(t)
        self.set_nowrap(t2)
        self.set_nowrap(t3)
        self.set_nowrap(t4)

        t2.write('set bugopen\n')
        self.expect('You are now open for bughouse.', t2)
        t.write('part guestefgh\n')
        self.expect('GuestABCD offers', t2)
        t2.write('part guestabcd\n')
        self.expect('GuestEFGH accepts', t)

        t4.write('set bugopen\n')
        self.expect('You are now open for bughouse.', t4)
        t3.write('part guestmnop\n')
        self.expect('GuestIJKL offers', t4)
        t4.write('a\n')
        self.expect('GuestMNOP accepts', t3)

        t.write('match guestijkl bughouse 3+0 w\n')
        self.expect('Issuing: GuestABCD (++++) [white] GuestIJKL (++++) unrated blitz bughouse 3 0', t)
        self.expect('Your bughouse partner issues: GuestABCD (++++) [white] GuestIJKL (++++) unrated blitz bughouse 3 0', t2)
        self.expect('Your game will be: GuestEFGH (++++) GuestMNOP (++++) unrated blitz bughouse 3 0', t2)
        self.expect('Challenge: GuestABCD (++++) [white] GuestIJKL (++++) unrated blitz bughouse 3 0', t3)
        self.expect('Your bughouse partner was challenged: GuestABCD (++++) [white] GuestIJKL (++++) unrated blitz bughouse 3 0', t4)
        self.expect('Your game will be: GuestEFGH (++++) GuestMNOP (++++) unrated blitz bughouse 3 0', t4)

        t3.write('a\n')
        self.expect('Creating:', t)
        self.expect('Creating:', t2)
        self.expect('Creating:', t3)
        self.expect('Creating:', t4)

        t.write('res\n')
        self.expect('GuestABCD resigns} 0-1', t)
        self.expect('GuestABCD resigns} 0-1', t3)
        self.expect("GuestMNOP's partner won} 1-0", t2)
        self.expect("GuestMNOP's partner won} 1-0", t4)

        self.close(t)
        self.close(t2)
        self.close(t3)
        self.close(t4)

    def test_draw_agreement(self):
        t = self.connect_as_guest('GuestABCD')
        t2 = self.connect_as_guest('GuestEFGH')
        t3 = self.connect_as_guest('GuestIJKL')
        t4 = self.connect_as_guest('GuestMNOP')

        self.set_nowrap(t)
        self.set_nowrap(t2)
        self.set_nowrap(t3)
        self.set_nowrap(t4)

        t2.write('set bugopen\n')
        self.expect('You are now open for bughouse.', t2)
        t.write('part guestefgh\n')
        self.expect('GuestABCD offers', t2)
        t2.write('part guestabcd\n')
        self.expect('GuestEFGH accepts', t)

        t4.write('set bugopen\n')
        self.expect('You are now open for bughouse.', t4)
        t3.write('part guestmnop\n')
        self.expect('GuestIJKL offers', t4)
        t4.write('a\n')
        self.expect('GuestMNOP accepts', t3)

        t.write('match guestijkl bughouse 3+0 w\n')
        self.expect('Issuing: GuestABCD (++++) [white] GuestIJKL (++++) unrated blitz bughouse 3 0', t)
        self.expect('Your bughouse partner issues: GuestABCD (++++) [white] GuestIJKL (++++) unrated blitz bughouse 3 0', t2)
        self.expect('Your game will be: GuestEFGH (++++) GuestMNOP (++++) unrated blitz bughouse 3 0', t2)
        self.expect('Challenge: GuestABCD (++++) [white] GuestIJKL (++++) unrated blitz bughouse 3 0', t3)
        self.expect('Your bughouse partner was challenged: GuestABCD (++++) [white] GuestIJKL (++++) unrated blitz bughouse 3 0', t4)
        self.expect('Your game will be: GuestEFGH (++++) GuestMNOP (++++) unrated blitz bughouse 3 0', t4)

        t3.write('a\n')
        self.expect('Creating:', t)
        self.expect('Creating:', t2)
        self.expect('Creating:', t3)
        self.expect('Creating:', t4)

        t3.write('draw\n')
        self.expect('GuestIJKL offers a draw.', t)
        t.write('draw\n')
        self.expect('drawn by agreement} 1/2-1/2', t)
        self.expect('drawn by agreement} 1/2-1/2', t3)
        self.expect("Partners' game drawn} 1/2-1/2", t2)
        self.expect("Partners' game drawn} 1/2-1/2", t4)

        self.close(t)
        self.close(t2)
        self.close(t3)
        self.close(t4)

class TestBpgn(Test):
    def test_bpgn(self):
        t = self.connect_as_guest('GuestABCD')
        t2 = self.connect_as_guest('GuestEFGH')
        t3 = self.connect_as_guest('GuestIJKL')
        t4 = self.connect_as_guest('GuestMNOP')

        t.write('set style 12\n')
        t2.write('set style 12\n')
        t3.write('set style 12\n')
        t4.write('set style 12\n')

        t2.write('set bugopen\n')
        self.expect('You are now open for bughouse.', t2)
        t.write('part guestefgh\n')
        self.expect('GuestABCD offers', t2)
        t2.write('part guestabcd\n')
        self.expect('GuestEFGH accepts', t)

        t4.write('set bugopen\n')
        self.expect('You are now open for bughouse.', t4)
        t3.write('part guestmnop\n')
        self.expect('GuestIJKL offers', t4)
        t4.write('a\n')
        self.expect('GuestMNOP accepts', t3)

        f = open('../data/bughouse.bpgn', 'r')

        bpgn = Bpgn(f)
        for g in bpgn:
            print 'game %s' % g
            t.write('match GuestIJKL bughouse white 1+0\n')
            self.expect('Issuing:', t)
            self.expect('Challenge:', t3)
            t3.write('accept\n')
            self.expect('<12> ', t)
            self.expect('<12> ', t2)
            self.expect('<12> ', t3)
            self.expect('<12> ', t4)

            # board A is t vs. t3; board B is t2 vs. t4
            for mv in g.moves:
                #print '%s. %s' % (mv.char, mv.text)
                if mv.char == 'A':
                    t.write('%s%s\n' % (mv.text, mv.decorator))
                    self.expect('<12> ', t)
                    self.expect('<12> ', t3)
                elif mv.char == 'B':
                    t4.write('%s%s\n' % (mv.text, mv.decorator))
                    self.expect('<12> ', t2)
                    self.expect('<12> ', t4)
                elif mv.char == 'a':
                    t3.write('%s%s\n' % (mv.text, mv.decorator))
                    self.expect('<12> ', t)
                    self.expect('<12> ', t3)
                elif mv.char == 'b':
                    t2.write('%s%s\n' % (mv.text, mv.decorator))
                    self.expect('<12> ', t2)
                    self.expect('<12> ', t4)

            if g.is_checkmate:
                assert(g.mated)
                if g.mated == 'A':
                    assert(g.result == '0-1')
                    self.expect("GuestABCD checkmated} 0-1", t)
                    self.expect("GuestABCD checkmated} 0-1", t3)
                    self.expect("GuestMNOP's partner won} 1-0", t2)
                    self.expect("GuestMNOP's partner won} 1-0", t4)
                elif g.mated == 'a':
                    assert(g.result == '1-0')
                    self.expect("GuestIJKL checkmated} 1-0", t)
                    self.expect("GuestIJKL checkmated} 1-0", t3)
                    self.expect("GuestEFGH's partner won} 0-1", t2)
                    self.expect("GuestEFGH's partner won} 0-1", t4)
                elif g.mated == 'B':
                    assert(g.result == '1-0')
                    self.expect("GuestABCD's partner won} 1-0", t)
                    self.expect("GuestABCD's partner won} 1-0", t3)
                    self.expect("GuestMNOP checkmated} 0-1", t2)
                    self.expect("GuestMNOP checkmated} 0-1", t4)
                elif g.mated == 'b':
                    assert(g.result == '0-1')
                    self.expect("GuestIJKL's partner won} 0-1", t)
                    self.expect("GuestIJKL's partner won} 0-1", t3)
                    self.expect("GuestEFGH checkmated} 1-0", t2)
                    self.expect("GuestEFGH checkmated} 1-0", t4)
                else:
                    assert(False)
            elif g.result == '1/2-1/2' and g.is_stalemate:
                self.expect('} 1/2-1/2', t)
                self.expect('} 1/2-1/2', t2)
                self.expect('} 1/2-1/2', t3)
                self.expect('} 1/2-1/2', t4)
            elif g.result == '1/2-1/2' and g.is_repetition:
                t.write('draw\n')
                t2.write('draw\n')
                self.expect('} 1/2-1/2', t)
                self.expect('} 1/2-1/2', t2)
                self.expect('} 1/2-1/2', t3)
                self.expect('} 1/2-1/2', t4)
            else:
                # result we can't check
                t.write('abo\n')
                t2.write('abo\n')
                t3.write('abo\n')
                t4.write('abo\n')
                self.expect('aborted', t)

        self.close(t)
        self.close(t2)
        self.close(t3)
        self.close(t4)

class TestBughouseRules(Test):
    def test_double_checkmate(self):
        t = self.connect_as_guest('GuestABCD')
        t2 = self.connect_as_guest('GuestEFGH')
        t3 = self.connect_as_guest('GuestIJKL')
        t4 = self.connect_as_guest('GuestMNOP')

        t.write('set style 12\n')
        t2.write('set style 12\n')
        t3.write('set style 12\n')
        t4.write('set style 12\n')

        t2.write('set bugopen\n')
        self.expect('You are now open for bughouse.', t2)
        t.write('part guestefgh\n')
        self.expect('GuestABCD offers', t2)
        t2.write('part guestabcd\n')
        self.expect('GuestEFGH accepts', t)

        t4.write('set bugopen\n')
        self.expect('You are now open for bughouse.', t4)
        t3.write('part guestmnop\n')
        self.expect('GuestIJKL offers', t4)
        t4.write('a\n')
        self.expect('GuestMNOP accepts', t3)

        t.write('match GuestIJKL bughouse white 1+0\n')
        self.expect('Issuing:', t)
        self.expect('Challenge:', t3)
        t3.write('accept\n')
        self.expect('<12> ', t)
        self.expect('<12> ', t2)
        self.expect('<12> ', t3)
        self.expect('<12> ', t4)

        moves = ['e4', 'f5', 'h4', 'g5', 'Qh5']
        wtm = True
        for mv in moves:
            if wtm:
                t.write('%s\n' % mv)
            else:
                t3.write('%s\n' % mv)
            self.expect('<12> ', t)
            self.expect('<12> ', t3)
            wtm = not wtm

        self.expect_not('mated', t)

        wtm = True
        moves2 = ['f4', 'e5', 'g4', 'Qh4#']
        for mv in moves2:
            if wtm:
                t4.write('%s\n' % mv)
            else:
                t2.write('%s\n' % mv)
            self.expect('<12> ', t2)
            self.expect('<12> ', t4)
            wtm = not wtm

        self.expect(' (GuestABCD vs. GuestIJKL) GuestIJKL and GuestMNOP checkmated} 1-0', t)
        self.expect(' (GuestABCD vs. GuestIJKL) GuestIJKL and GuestMNOP checkmated} 1-0', t3)
        self.expect(' (GuestMNOP vs. GuestEFGH) GuestIJKL and GuestMNOP checkmated} 0-1', t2)
        self.expect(' (GuestMNOP vs. GuestEFGH) GuestIJKL and GuestMNOP checkmated} 0-1', t4)

        self.close(t)
        self.close(t2)
        self.close(t3)
        self.close(t4)

    def test_contact_mate(self):
        t = self.connect_as_guest('GuestABCD')
        t2 = self.connect_as_guest('GuestEFGH')
        t3 = self.connect_as_guest('GuestIJKL')
        t4 = self.connect_as_guest('GuestMNOP')

        t.write('set style 12\n')
        t2.write('set style 12\n')
        t3.write('set style 12\n')
        t4.write('set style 12\n')

        t2.write('set bugopen\n')
        self.expect('You are now open for bughouse.', t2)
        t.write('part guestefgh\n')
        self.expect('GuestABCD offers', t2)
        t2.write('part guestabcd\n')
        self.expect('GuestEFGH accepts', t)

        t4.write('set bugopen\n')
        self.expect('You are now open for bughouse.', t4)
        t3.write('part guestmnop\n')
        self.expect('GuestIJKL offers', t4)
        t4.write('a\n')
        self.expect('GuestMNOP accepts', t3)

        t.write('match GuestIJKL bughouse white 1+0\n')
        self.expect('Issuing:', t)
        self.expect('Challenge:', t3)
        t3.write('accept\n')
        self.expect('<12> ', t)
        self.expect('<12> ', t2)
        self.expect('<12> ', t3)
        self.expect('<12> ', t4)

        moves = ['e4', 'e5', 'Qh5', 'Nc6', 'Bc4', 'Nf6', 'Qxf7#']
        wtm = True
        for mv in moves:
            if wtm:
                t.write('%s\n' % mv)
            else:
                t3.write('%s\n' % mv)
            self.expect('<12> ', t)
            self.expect('<12> ', t3)
            wtm = not wtm

        self.expect(' (GuestABCD vs. GuestIJKL) GuestIJKL checkmated} 1-0', t)
        self.expect(' (GuestABCD vs. GuestIJKL) GuestIJKL checkmated} 1-0', t3)
        self.expect(" (GuestMNOP vs. GuestEFGH) GuestEFGH's partner won} 0-1", t2)
        self.expect(" (GuestMNOP vs. GuestEFGH) GuestEFGH's partner won} 0-1", t4)

        self.close(t)
        self.close(t2)
        self.close(t3)
        self.close(t4)

    def test_draw_checkmate(self):
        t = self.connect_as_guest('GuestABCD')
        t2 = self.connect_as_guest('GuestEFGH')
        t3 = self.connect_as_guest('GuestIJKL')
        t4 = self.connect_as_guest('GuestMNOP')

        t.write('set style 12\n')
        t2.write('set style 12\n')
        t3.write('set style 12\n')
        t4.write('set style 12\n')

        t2.write('set bugopen\n')
        self.expect('You are now open for bughouse.', t2)
        t.write('part guestefgh\n')
        self.expect('GuestABCD offers', t2)
        t2.write('part guestabcd\n')
        self.expect('GuestEFGH accepts', t)

        t4.write('set bugopen\n')
        self.expect('You are now open for bughouse.', t4)
        t3.write('part guestmnop\n')
        self.expect('GuestIJKL offers', t4)
        t4.write('a\n')
        self.expect('GuestMNOP accepts', t3)

        t.write('match GuestIJKL bughouse white 1+0\n')
        self.expect('Issuing:', t)
        self.expect('Challenge:', t3)
        t3.write('accept\n')
        self.expect('<12> ', t)
        self.expect('<12> ', t2)
        self.expect('<12> ', t3)
        self.expect('<12> ', t4)

        moves = ['e4', 'f5', 'h4', 'g5', 'Qh5']
        wtm = True
        for mv in moves:
            if wtm:
                t.write('%s\n' % mv)
            else:
                t3.write('%s\n' % mv)
            self.expect('<12> ', t)
            self.expect('<12> ', t3)
            wtm = not wtm

        self.expect_not('mated', t)

        wtm = True
        for mv in moves:
            if wtm:
                t4.write('%s\n' % mv)
            else:
                t2.write('%s\n' % mv)
            self.expect('<12> ', t2)
            self.expect('<12> ', t4)
            wtm = not wtm

        self.expect(' (GuestABCD vs. GuestIJKL) Game drawn by mate on both boards} 1/2-1/2', t)
        self.expect(' (GuestABCD vs. GuestIJKL) Game drawn by mate on both boards} 1/2-1/2', t3)
        self.expect(' (GuestMNOP vs. GuestEFGH) Game drawn by mate on both boards} 1/2-1/2', t2)
        self.expect(' (GuestMNOP vs. GuestEFGH) Game drawn by mate on both boards} 1/2-1/2', t4)

        self.close(t)
        self.close(t2)
        self.close(t3)
        self.close(t4)

    def test_white_resign(self):
        t = self.connect_as_guest('GuestABCD')
        t2 = self.connect_as_guest('GuestEFGH')
        t3 = self.connect_as_guest('GuestIJKL')
        t4 = self.connect_as_guest('GuestMNOP')

        t.write('set style 12\n')
        t2.write('set style 12\n')
        t3.write('set style 12\n')
        t4.write('set style 12\n')

        t2.write('set bugopen\n')
        self.expect('You are now open for bughouse.', t2)
        t.write('part guestefgh\n')
        self.expect('GuestABCD offers', t2)
        t2.write('part guestabcd\n')
        self.expect('GuestEFGH accepts', t)

        t4.write('set bugopen\n')
        self.expect('You are now open for bughouse.', t4)
        t3.write('part guestmnop\n')
        self.expect('GuestIJKL offers', t4)
        t4.write('a\n')
        self.expect('GuestMNOP accepts', t3)

        t.write('match GuestIJKL bughouse white 1+0\n')
        self.expect('Issuing:', t)
        self.expect('Challenge:', t3)
        t3.write('accept\n')
        self.expect('<12> ', t)
        self.expect('<12> ', t2)
        self.expect('<12> ', t3)
        self.expect('<12> ', t4)

        t.write('res\n')

        self.expect('GuestABCD resigns} 0-1', t)
        self.expect('GuestABCD resigns} 0-1', t3)
        self.expect("GuestMNOP's partner won} 1-0", t2)
        self.expect("GuestMNOP's partner won} 1-0", t4)

        self.close(t)
        self.close(t2)
        self.close(t3)
        self.close(t4)

    def test_black_resign(self):
        t = self.connect_as_guest('GuestABCD')
        t2 = self.connect_as_guest('GuestEFGH')
        t3 = self.connect_as_guest('GuestIJKL')
        t4 = self.connect_as_guest('GuestMNOP')

        t.write('set style 12\n')
        t2.write('set style 12\n')
        t3.write('set style 12\n')
        t4.write('set style 12\n')

        t2.write('set bugopen\n')
        self.expect('You are now open for bughouse.', t2)
        t.write('part guestefgh\n')
        self.expect('GuestABCD offers', t2)
        t2.write('part guestabcd\n')
        self.expect('GuestEFGH accepts', t)

        t4.write('set bugopen\n')
        self.expect('You are now open for bughouse.', t4)
        t3.write('part guestmnop\n')
        self.expect('GuestIJKL offers', t4)
        t4.write('a\n')
        self.expect('GuestMNOP accepts', t3)

        t.write('match GuestIJKL bughouse white 1+0\n')
        self.expect('Issuing:', t)
        self.expect('Challenge:', t3)
        t3.write('accept\n')
        self.expect('<12> ', t)
        self.expect('<12> ', t2)
        self.expect('<12> ', t3)
        self.expect('<12> ', t4)

        t2.write('res\n')

        self.expect("GuestIJKL's partner won} 0-1", t)
        self.expect("GuestIJKL's partner won} 0-1", t3)
        self.expect("GuestEFGH resigns} 1-0", t2)
        self.expect("GuestEFGH resigns} 1-0", t4)

        self.close(t)
        self.close(t2)
        self.close(t3)
        self.close(t4)

    def test_draw_agreement(self):
        t = self.connect_as_guest('GuestABCD')
        t2 = self.connect_as_guest('GuestEFGH')
        t3 = self.connect_as_guest('GuestIJKL')
        t4 = self.connect_as_guest('GuestMNOP')

        t.write('set style 12\n')
        t2.write('set style 12\n')
        t3.write('set style 12\n')
        t4.write('set style 12\n')

        t2.write('set bugopen\n')
        self.expect('You are now open for bughouse.', t2)
        t.write('part guestefgh\n')
        self.expect('GuestABCD offers', t2)
        t2.write('part guestabcd\n')
        self.expect('GuestEFGH accepts', t)

        t4.write('set bugopen\n')
        self.expect('You are now open for bughouse.', t4)
        t3.write('part guestmnop\n')
        self.expect('GuestIJKL offers', t4)
        t4.write('a\n')
        self.expect('GuestMNOP accepts', t3)

        t.write('match GuestIJKL bughouse white 1+0\n')
        self.expect('Issuing:', t)
        self.expect('Challenge:', t3)
        t3.write('accept\n')
        self.expect('<12> ', t)
        self.expect('<12> ', t2)
        self.expect('<12> ', t3)
        self.expect('<12> ', t4)

        t2.write('draw\n')
        self.expect('GuestEFGH offers a draw.', t4)
        t4.write('acc\n')
        self.expect("Partners' game drawn} 1/2-1/2", t)
        self.expect("Partners' game drawn} 1/2-1/2", t3)
        self.expect('Game drawn by agreement} 1/2-1/2', t2)
        self.expect('Game drawn by agreement} 1/2-1/2', t4)

        self.close(t)
        self.close(t2)
        self.close(t3)
        self.close(t4)

    def test_stalemate(self):
        """ very rare, but can happen """
        t = self.connect_as_guest('GuestABCD')
        t2 = self.connect_as_guest('GuestEFGH')
        t3 = self.connect_as_guest('GuestIJKL')
        t4 = self.connect_as_guest('GuestMNOP')

        t.write('set style 12\n')
        t2.write('set style 12\n')
        t3.write('set style 12\n')
        t4.write('set style 12\n')

        t2.write('set bugopen\n')
        self.expect('You are now open for bughouse.', t2)
        t.write('part guestefgh\n')
        self.expect('GuestABCD offers', t2)
        t2.write('part guestabcd\n')
        self.expect('GuestEFGH accepts', t)

        t4.write('set bugopen\n')
        self.expect('You are now open for bughouse.', t4)
        t3.write('part guestmnop\n')
        self.expect('GuestIJKL offers', t4)
        t4.write('a\n')
        self.expect('GuestMNOP accepts', t3)

        t.write('match GuestIJKL bughouse white 1+0\n')
        self.expect('Issuing:', t)
        self.expect('Challenge:', t3)
        t3.write('accept\n')
        self.expect('<12> ', t)
        self.expect('<12> ', t2)
        self.expect('<12> ', t3)
        self.expect('<12> ', t4)

        # by Sam Loyd
        moves = ['d4', 'd6', 'Qd2', 'e5', 'a4', 'e4', 'Qf4', 'f5', 'h3',
            'Be7', 'Qh2', 'Be6', 'Ra3', 'c5', 'Rg3', 'Qa5+', 'Nd2', 'Bh4',
            'f3', 'Bb3', 'd5', 'e3', 'c4', 'f4']
        wtm = True
        for mv in moves:
            if wtm:
                t.write('%s\n' % mv)
            else:
                t3.write('%s\n' % mv)
            self.expect('<12> ', t)
            self.expect('<12> ', t3)
            wtm = not wtm

        self.expect_not('mated', t)

        wtm = True
        for mv in moves:
            if wtm:
                t4.write('%s\n' % mv)
            else:
                t2.write('%s\n' % mv)
            self.expect('<12> ', t2)
            self.expect('<12> ', t4)
            wtm = not wtm

        self.expect(' (GuestABCD vs. GuestIJKL) Game drawn by stalemate} 1/2-1/2', t)
        self.expect(' (GuestABCD vs. GuestIJKL) Game drawn by stalemate} 1/2-1/2', t3)
        self.expect(' (GuestMNOP vs. GuestEFGH) Game drawn by stalemate} 1/2-1/2', t2)
        self.expect(' (GuestMNOP vs. GuestEFGH) Game drawn by stalemate} 1/2-1/2', t4)

        self.close(t)
        self.close(t2)
        self.close(t3)
        self.close(t4)

    def test_stalemate_and_checkmate(self):
        t = self.connect_as_guest('GuestABCD')
        t2 = self.connect_as_guest('GuestEFGH')
        t3 = self.connect_as_guest('GuestIJKL')
        t4 = self.connect_as_guest('GuestMNOP')

        t.write('set style 12\n')
        t2.write('set style 12\n')
        t3.write('set style 12\n')
        t4.write('set style 12\n')

        t2.write('set bugopen\n')
        self.expect('You are now open for bughouse.', t2)
        t.write('part guestefgh\n')
        self.expect('GuestABCD offers', t2)
        t2.write('part guestabcd\n')
        self.expect('GuestEFGH accepts', t)

        t4.write('set bugopen\n')
        self.expect('You are now open for bughouse.', t4)
        t3.write('part guestmnop\n')
        self.expect('GuestIJKL offers', t4)
        t4.write('a\n')
        self.expect('GuestMNOP accepts', t3)

        t.write('match GuestIJKL bughouse white 1+0\n')
        self.expect('Issuing:', t)
        self.expect('Challenge:', t3)
        t3.write('accept\n')
        self.expect('<12> ', t)
        self.expect('<12> ', t2)
        self.expect('<12> ', t3)
        self.expect('<12> ', t4)

        # by Sam Loyd
        moves = ['d4', 'd6', 'Qd2', 'e5', 'a4', 'e4', 'Qf4', 'f5', 'h3',
            'Be7', 'Qh2', 'Be6', 'Ra3', 'c5', 'Rg3', 'Qa5+', 'Nd2', 'Bh4',
            'f3', 'Bb3', 'd5', 'e3', 'c4', 'f4']
        wtm = True
        for mv in moves:
            if wtm:
                t.write('%s\n' % mv)
            else:
                t3.write('%s\n' % mv)
            self.expect('<12> ', t)
            self.expect('<12> ', t3)
            wtm = not wtm

        self.expect_not('mated', t)

        moves2 = ['e4', 'f5', 'h4', 'g5', 'Qh5']
        wtm = True
        for mv in moves2:
            if wtm:
                t4.write('%s\n' % mv)
            else:
                t2.write('%s\n' % mv)
            self.expect('<12> ', t2)
            self.expect('<12> ', t4)
            wtm = not wtm

        self.expect(" (GuestABCD vs. GuestIJKL) GuestIJKL's partner won} 0-1", t)
        self.expect(" (GuestABCD vs. GuestIJKL) GuestIJKL's partner won} 0-1", t3)
        self.expect(' (GuestMNOP vs. GuestEFGH) GuestEFGH checkmated} 1-0', t2)
        self.expect(' (GuestMNOP vs. GuestEFGH) GuestEFGH checkmated} 1-0', t4)

        self.close(t)
        self.close(t2)
        self.close(t3)
        self.close(t4)

    def test_checkmate_and_stalemate(self):
        t = self.connect_as_guest('GuestABCD')
        t2 = self.connect_as_guest('GuestEFGH')
        t3 = self.connect_as_guest('GuestIJKL')
        t4 = self.connect_as_guest('GuestMNOP')

        t.write('set style 12\n')
        t2.write('set style 12\n')
        t3.write('set style 12\n')
        t4.write('set style 12\n')

        t2.write('set bugopen\n')
        self.expect('You are now open for bughouse.', t2)
        t.write('part guestefgh\n')
        self.expect('GuestABCD offers', t2)
        t2.write('part guestabcd\n')
        self.expect('GuestEFGH accepts', t)

        t4.write('set bugopen\n')
        self.expect('You are now open for bughouse.', t4)
        t3.write('part guestmnop\n')
        self.expect('GuestIJKL offers', t4)
        t4.write('a\n')
        self.expect('GuestMNOP accepts', t3)

        t.write('match GuestIJKL bughouse white 1+0\n')
        self.expect('Issuing:', t)
        self.expect('Challenge:', t3)
        t3.write('accept\n')
        self.expect('<12> ', t)
        self.expect('<12> ', t2)
        self.expect('<12> ', t3)
        self.expect('<12> ', t4)

        moves = ['f4', 'e5', 'g4', 'Qh4#']
        wtm = True
        for mv in moves:
            if wtm:
                t.write('%s\n' % mv)
            else:
                t3.write('%s\n' % mv)
            self.expect('<12> ', t)
            self.expect('<12> ', t3)
            wtm = not wtm

        self.expect_not('mated', t)

        # by Sam Loyd
        moves2 = ['d4', 'd6', 'Qd2', 'e5', 'a4', 'e4', 'Qf4', 'f5', 'h3',
            'Be7', 'Qh2', 'Be6', 'Ra3', 'c5', 'Rg3', 'Qa5+', 'Nd2', 'Bh4',
            'f3', 'Bb3', 'd5', 'e3', 'c4', 'f4']
        wtm = True
        for mv in moves2:
            if wtm:
                t4.write('%s\n' % mv)
            else:
                t2.write('%s\n' % mv)
            self.expect('<12> ', t2)
            self.expect('<12> ', t4)
            wtm = not wtm

        self.expect(" (GuestABCD vs. GuestIJKL) GuestABCD checkmated} 0-1", t)
        self.expect(" (GuestABCD vs. GuestIJKL) GuestABCD checkmated} 0-1", t3)
        self.expect(" (GuestMNOP vs. GuestEFGH) GuestMNOP's partner won} 1-0", t2)
        self.expect(" (GuestMNOP vs. GuestEFGH) GuestMNOP's partner won} 1-0", t4)

        self.close(t)
        self.close(t2)
        self.close(t3)
        self.close(t4)

    def test_bughouse_b1_line(self):
        t = self.connect_as_guest('GuestABCD')
        t2 = self.connect_as_guest('GuestEFGH')
        t3 = self.connect_as_guest('GuestIJKL')
        t4 = self.connect_as_guest('GuestMNOP')

        t.write('set style 12\n')
        t2.write('set style 12\n')
        t3.write('set style 12\n')
        t4.write('set style 12\n')

        t2.write('set bugopen\n')
        self.expect('You are now open for bughouse.', t2)
        t.write('part guestefgh\n')
        self.expect('GuestABCD offers', t2)
        t2.write('part guestabcd\n')
        self.expect('GuestEFGH accepts', t)

        t4.write('set bugopen\n')
        self.expect('You are now open for bughouse.', t4)
        t3.write('part guestmnop\n')
        self.expect('GuestIJKL offers', t4)
        t4.write('a\n')
        self.expect('GuestMNOP accepts', t3)

        t.write('match GuestIJKL bughouse white 1+0\n')
        self.expect('Issuing:', t)
        self.expect('Challenge:', t3)
        t3.write('accept\n')
        self.expect('<12> ', t)
        self.expect('<12> ', t2)
        self.expect('<12> ', t3)
        self.expect('<12> ', t4)

        t.write('e4\n')
        self.expect('<12> ', t)
        self.expect('<b1> game 1 white [] black []', t)
        self.expect('<12> ', t3)
        self.expect('<b1> game 1 white [] black []', t3)

        self.close(t)
        self.close(t2)
        self.close(t3)
        self.close(t4)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
