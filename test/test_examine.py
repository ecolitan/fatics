from test import *

class TestExamine(Test):
    def test_examine(self):
        t = self.connect_as_user('GuestPQLQ', '')

        t.write('forward\n')
        self.expect('You are not examining a game', t)

        t.write('examine\n')
        self.expect('Starting a game in examine (scratch) mode.', t)

        t.write('examine\n')
        self.expect('You are already examining a game.', t)

        #You're at the end of the game.
        #12> rnbqkbnr pppppppp -------- -------- -------- -------- PPPPPPPP RNBQKBNR W -1 1 1 1 1 0 340 GuestPQLQ GuestPQLQ 2 0 0 39 39 0 0 1 none (0:00) none 0 0 0
        #fics% e2e4
        #<12> rnbqkbnr pppppppp -------- -------- ----P--- -------- PPPP-PPP RNBQKBNR B 4 1 1 1 1 0 340 GuestPQLQ GuestPQLQ 2 0 0 39 39 0 0 1 P/e2-e4 (0:00) e4 0 0 0
        self.close(t)


# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
