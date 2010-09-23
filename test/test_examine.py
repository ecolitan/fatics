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

import time

class TestExamine(Test):
    def test_examine_scratch(self):
        t = self.connect_as('GuestPQLQ', '')

        t.write('forward\n')
        self.expect('You are not examining a game', t)

        t.write('backward\n')
        self.expect('You are not examining a game', t)

        t.write('examine\n')
        self.expect('Starting a game in examine (scratch) mode.', t)
        self.expect('<12> rnbqkbnr pppppppp -------- -------- -------- -------- PPPPPPPP RNBQKBNR W -1 1 1 1 1 0 1 GuestPQLQ GuestPQLQ 2 0 0 39 39 0 0 1 none (0:00) none 0 0 0', t)

        t.write('forward\n')
        self.expect("You're at the end of the game.", t)
        t.write('backward\n')
        self.expect("You're at the beginning of the game.", t)

        t.write('examine\n')
        self.expect('You are already examining a game.', t)

        t.write('abort\n')
        self.expect('You are not playing a game.', t)

        t.write('e2e5\n')
        self.expect('Illegal move (e2e5)', t)

        t.write('e2e4\n')
        # difference from fics: en passant file is -1 despite the last move
        # being a double push, since there is no legal en passant capture
        self.expect('<12> rnbqkbnr pppppppp -------- -------- ----P--- -------- PPPP-PPP RNBQKBNR B -1 1 1 1 1 0 1 GuestPQLQ GuestPQLQ 2 0 0 39 39 0 0 1 P/e2-e4 (0:00) e4 0 0 0', t)
        self.expect('GuestPQLQ moves: e4', t)

        t.write('forward\n')
        self.expect("You're at the end of the game.", t)

        t.write('backward\n')
        self.expect('GuestPQLQ backs up 1 move.', t)

        self.close(t)

    @with_player('testplayer', 'testpass')
    def test_examine_history(self):
        t = self.connect_as_admin()
        t2 = self.connect_as('testplayer', 'testpass')

        t.write('set style 12\n')
        t2.write('set style 12\n')
        t.write('aclearhist admin\n')
        self.expect('History of admin cleared.', t)

        t.write('ex testplayer -1\n')
        self.expect('testplayer has no history games.', t)

        t.write('match testplayer 2 12 white zh u\n')
        self.expect('Challenge:', t2)
        t2.write('a\n')
        self.expect('<12> ', t)
        self.expect('<12> ', t2)

        moves = ['e4', 'f5', 'h4', 'g5', 'Qh5#']
        wtm = True
        for mv in moves:
            if wtm:
                t.write('%s\n' % mv)
            else:
                t2.write('%s\n' % mv)
            self.expect('<12> ', t)
            self.expect('<12> ', t2)
            wtm = not wtm

        self.expect('testplayer checkmated} 1-0', t)
        self.expect('testplayer checkmated} 1-0', t2)

        t.write('ex admin 99\n')
        self.expect('There is no history game 99 for admin.', t)

        # negative game number
        t.write('ex admin -1\n')
        self.expect('<12> ', t)
        t.write('forward 9999\n')
        self.expect('testplayer checkmated 1-0', t)
        t.write('unex\n')
        self.expect('You are no longer examining game 1.', t)

        t.write('match testplayer 2 12 white u\n')
        self.expect('Challenge: ', t2)
        t2.write('a\n')
        self.expect('<12> ', t)
        self.expect('<12> ', t2)
        t2.write('resign\n')
        self.expect('testplayer resigns} 1-0', t)
        self.expect('testplayer resigns} 1-0', t2)

        t.write('match testplayer 2 12 white u\n')
        self.expect('Challenge: ', t2)
        t2.write('a\n')
        self.expect('Creating: ', t)
        self.expect('Creating: ', t2)
        self.expect('<12> ', t)
        self.expect('<12> ', t2)
        t.write('e4\n')
        self.expect('<12> ', t)
        self.expect('<12> ', t2)
        t.write('resign\n')
        self.expect('admin resigns} 0-1', t)
        self.expect('admin resigns} 0-1', t2)

        # non-negative game number
        t.write('ex admin 0\n')
        self.expect('<12> ', t)
        t.write('forward 9999\n')
        self.expect('testplayer checkmated 1-0', t)
        t.write('unex\n')
        self.expect('You are no longer examining game 1.', t)

        t.write('ex admin 2\n')
        self.expect('<12> ', t)
        t.write('forward 1\n')
        self.expect('admin resigns 0-1', t)

        t.write('match testplayer\n')
        self.expect("You can't challenge while you are examining", t)

        t.write('unex\n')
        self.expect('You are no longer examining game 1.', t)

        t.write('aclearhist admin\n')
        self.expect('History of admin cleared.', t)
        t.write('aclearhist testplayer\n')
        self.expect('History of testplayer cleared.', t)

        self.close(t)

    def test_examine_moves(self):
        t = self.connect_as('GuestABCD', '')

        t.write('iset ms 1\n')
        t.write('ex\n')
        self.expect('Starting a game in examine (scratch) mode.', t)
        t.write('e4\n')
        t.write('e5\n')
        t.write('f4\n')
        t.write('moves\n')

        # original FICS would send "GuestABCD (UNR) vs. GuestABCD (UNR)" here
        self.expect('Movelist for game 1:\r\n\r\nGuestABCD (++++) vs. GuestABCD (++++) --- ', t)
        self.expect('Unrated untimed match, initial time: 0 minutes, increment: 0 seconds.', t)
        self.expect('Move  GuestABCD               GuestABCD', t)
        self.expect('----  ---------------------   ---------------------', t)
        self.expect('  1.  e4      (0:00.000)      e5      (0:00.000)', t)
        self.expect('  2.  f4      (0:00.000)', t)
        self.expect('      {Still in progress} *', t)

        self.close(t)

    def test_examine_checkmate(self):
        moves = ['e4', 'f5', 'h4', 'g5', 'Qh5#']
        self._assert_game_is_legal(moves, 'Game 1: Black checkmated 1-0')

    def test_examine_stalemate(self):
        # game by Sam Loyd
        moves = ['e3', 'a5', 'Qh5', 'Ra6', 'Qxa5', 'h5', 'Qxc7', 'Rah6',
            'h4', 'f6', 'Qxd7+', 'Kf7', 'Qxb7', 'Qd3', 'Qxb8', 'Qh7',
            'Qxc8', 'Kg6', 'Qe6']
        self._assert_game_is_legal(moves, 'Game 1: Game drawn by stalemate 1/2-1/2')

    def _assert_game_is_legal(self, moves, result=None):
        t = self.connect_as('GuestWXYZ', '')
        t.write('ex\n')
        for mv in moves:
            t.write('%s\n' % mv)
            self.expect('Game 1: GuestWXYZ moves: %s\r\n' % mv, t)

        if result is not None:
            self.expect(result, t)
        t.write('unex\n')

        self.close(t)

    def test_playing_commands(self):
        t = self.connect_as_guest()

        t.write('ex\n')
        self.expect('Starting a game', t)

        t.write('abort\n')
        self.expect('You are not playing a game.', t)

        t.write('draw\n')
        self.expect('You are not playing a game.', t)

        t.write('resign\n')
        self.expect('You are not playing a game.', t)

        t.write('unex\n')
        self.expect('no longer examining', t)

        self.close(t)

class TestUnexamine(Test):
    def test_unexamine(self):
        t = self.connect_as_guest()
        t.write('ex\n')
        t.write('unex\n')
        self.expect('You are no longer examining game 1.', t)

        t.write('unex\n')
        self.expect('You are not examining a game.', t)
        t.write('unex 1\n')
        self.expect('Usage: ', t)

        self.close(t)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
