from test import *

import time

class TestExamine(Test):
    def test_examine(self):
        t = self.connect_as_user('GuestPQLQ', '')

        t.write('forward\n')
        self.expect('You are not examining a game', t)

        t.write('examine\n')
        self.expect('Starting a game in examine (scratch) mode.', t)
        self.expect('<12> rnbqkbnr pppppppp -------- -------- -------- -------- PPPPPPPP RNBQKBNR W -1 1 1 1 1 0 1 GuestPQLQ GuestPQLQ 2 0 0 39 39 0 0 1 none (0:00) none 0 0 0', t)

        t.write('examine\n')
        self.expect('You are already examining a game.', t)

        t.write('abort\n')
        self.expect('You are not playing a game.', t)

        t.write('e2e5\n')
        self.expect('Illegal move (e2e5)', t)

        t.write('e2e4\n')
        # diffference from fics: en passant file is -1 despite the last move
        # being a double push, since there is no legal en passant capture
        self.expect('<12> rnbqkbnr pppppppp -------- -------- ----P--- -------- PPPP-PPP RNBQKBNR B -1 1 1 1 1 0 1 GuestPQLQ GuestPQLQ 2 0 0 39 39 0 0 1 P/e2-e4 (0:00) e4 0 0 0', t)
        self.expect('GuestPQLQ moves: e4', t)

        #time.sleep(3)
        #You're at the end of the game.

        self.close(t)

    def test_examine_checkmate(self):
        moves = ['e4', 'f5', 'h4', 'g5', 'Qh5#']
        self._assert_game_is_legal(moves, 'Game 1: Black checkmated 1-0')

    def _assert_game_is_legal(self, moves, result=None):
        t = self.connect_as_user('GuestWXYZ', '')
        t.write('ex\n')
        for mv in moves:
            t.write('%s\n' % mv)
            self.expect('Game 1: GuestWXYZ moves: %s\r\n' % mv, t)

        if result is not None:
            self.expect(result, t)
        t.write('unex\n')

        self.close(t)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
