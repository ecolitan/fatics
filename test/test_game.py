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

class TestGame(Test):
    def test_game_basics(self):
        t = self.connect_as_guest('GuestABCD')
        t2 = self.connect_as_admin()

        t.write('match admin white 1 0\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('Creating: GuestABCD (++++) admin (----) unrated lightning 1 0', t)
        self.expect('Creating: GuestABCD (++++) admin (----) unrated lightning 1 0', t2)

        self.expect('{Game 1 (GuestABCD vs. admin) Creating unrated lightning match.}', t)
        self.expect('{Game 1 (GuestABCD vs. admin) Creating unrated lightning match.}', t2)

        t2.write('e7e5\n')
        self.expect('not your move', t2)

        t2.write('e2e5\n')
        self.expect('not your move', t2)

        # plain illegal move
        t.write('e2e5\n')
        self.expect('Illegal move (e2e5).', t)

        t.write('e7e5\n')
        self.expect('Illegal move (e7e5).', t)

        t.write('e3e4\n')
        self.expect('Illegal move (e3e4).', t)

        # square occpied by own piece
        t.write('a1a2\n')
        self.expect('Illegal move (a1a2).', t)

        # path blocked by own piece
        t.write('a1a3\n')
        self.expect('Illegal move (a1a3).', t)

        # legal move
        t.write('e2e4\n')
        self.expect_not('Illegal move', t)

        t2.write('e7e5\n')
        self.expect_not('Illegal move', t2)

        t.write('g1f3\n')
        self.expect_not('Illegal move', t)

        t2.write('b8c6\n')
        self.expect_not('Illegal move', t2)

        # castling blocked
        t.write('O-O\n')
        self.expect('Illegal move', t)
        t.write('O-O-O\n')
        self.expect('Illegal move', t)

        t.write('f1c4\n')
        self.expect_not('Illegal move', t2)

        t2.write('g8f6\n')
        self.expect_not('Illegal move', t2)

        t.write('O-O\n')
        self.expect_not('Illegal move', t2)

        self.close(t)
        self.close(t2)

    def _assert_game_is_legal(self, moves, result=None):
        t = self.connect_as_guest('GuestABCD')
        t2 = self.connect_as_admin()
        t.write('set style 12\n')
        t2.write('set style 12\n')

        t.write('match admin white 1 0\n')
        self.expect('Issuing:', t)
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('<12> ', t)
        self.expect('<12> ', t2)

        wtm = True
        for mv in moves:
            if wtm:
                t.write('%s\n' % mv)
            else:
                t2.write('%s\n' % mv)
            self.expect('<12> ', t)
            self.expect('<12> ', t2)
            wtm = not wtm
        if result is not None:
            self.expect(result, t)
            self.expect(result, t2)
        else:
            t.write('abort\n')
            t2.write('abort\n')

        self.close(t)
        self.close(t2)

    def test_lalg(self):
        moves = ['g2g3', 'b7b6', 'f1g2', 'b8c6', 'g1f3', 'c8b7', 'e1g1',
            'e7e6', 'd2d4', 'd8e7', 'c1f4', 'e8c8']
        self._assert_game_is_legal(moves)

    def test_promotion(self):
        moves = ['d4', 'd5', 'c4', 'c6', 'Nf3', 'Nf6', 'e3', 'Bf5', 'Qb3',
            'Qb6', 'cxd5', 'Qxb3', 'axb3', 'Bxb1', 'dxc6', 'Be4', 'Rxa7',
            'Rxa7','c7', 'Nc6', 'c8=Q+']
        self._assert_game_is_legal(moves)

    def test_promotion_lalg(self):
        moves = ['d4', 'd5', 'c4', 'c6', 'Nf3', 'Nf6', 'e3', 'Bf5', 'Qb3',
            'Qb6', 'cxd5', 'Qxb3', 'axb3', 'Bxb1', 'dxc6', 'Be4', 'Rxa7',
            'Rxa7','c7', 'Nc6', 'c7c8=q']
        self._assert_game_is_legal(moves)

    def test_promotion_assumes_queen(self):
        moves = ['d4', 'd5', 'c4', 'c6', 'Nf3', 'Nf6', 'e3', 'Bf5', 'Qb3',
            'Qb6', 'cxd5', 'Qxb3', 'axb3', 'Bxb1', 'dxc6', 'Be4', 'Rxa7',
            'Rxa7','c7', 'Nc6', 'c8', 'Nd8', 'Qxd8']
        self._assert_game_is_legal(moves)

    def test_san_basic(self):
        t = self.connect_as_guest()
        t2 = self.connect_as_admin()

        t.write('match admin white 1 0\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('Creating: ', t)
        self.expect('Creating: ', t2)

        t.write('e5\n')
        self.expect('Illegal move', t)

        t.write('e4\n')
        self.expect_not('Illegal move', t)

        self.close(t)
        self.close(t2)

    def test_illegal_move(self):
        t = self.connect_as_guest()
        t2 = self.connect_as_admin()

        t.write('set style 12\n')
        self.expect('Style 12 set.', t)
        t2.write('set style 12\n')
        self.expect('Style 12 set.', t2)

        t.write('match admin white 1 0\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('Creating: ', t)
        self.expect('Creating: ', t2)

        self.expect('<12> ', t)
        self.expect('<12> ', t2)

        t.write('e4\n')
        self.expect('<12> ', t)
        self.expect('<12> ', t2)

        t2.write('e4\n')
        self.expect('Illegal move (e4).', t2)
        # the style12 string should be re-sent (eboard depends on this)
        self.expect('<12> ', t2)

        t2.write('abort\n')
        self.expect('aborted', t)

        self.close(t)
        self.close(t2)

    def test_san_check(self):
        t = self.connect_as_guest()
        t2 = self.connect_as_admin()
        t.write('set style 12\n')
        t2.write('set style 12\n')

        t.write('match admin white 1 0\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('Creating: ', t)
        self.expect('Creating: ', t2)

        t.write('e4\n')
        self.expect('<12> ', t)
        self.expect('<12> ', t2)

        t2.write('e5\n')
        self.expect('<12> ', t)
        self.expect('<12> ', t2)

        t.write('f3\n')
        self.expect('<12> ', t)
        self.expect('f3', t)
        self.expect('<12> ', t2)
        self.expect('f3', t2)

        t2.write('Qh4\n')
        self.expect('Qh4+', t)
        self.expect('Qh4+', t2)

        self.close(t)
        self.close(t2)

    def test_san_checkmate(self):
        moves = ['f3', 'e5', 'g4', 'Qh4']
        self._assert_game_is_legal(moves, 'checkmated} 0-1')

    def test_san_stalemate(self):
        # by Sam Loyd
        moves = ['e3', 'a5', 'Qh5', 'Ra6', 'Qxa5', 'h5', 'Qxc7', 'Rah6', 'h4', 'f6', 'Qxd7+', 'Kf7', 'Qxb7', 'Qd3', 'Qxb8', 'Qh7', 'Qxc8', 'Kg6', 'Qe6']
        self._assert_game_is_legal(moves, 'drawn by stalemate} 1/2-1/2')

    def test_draw_repetition(self):
        t = self.connect_as_guest('GuestABCD')
        t2 = self.connect_as_admin()

        t.write('set style 12\n')
        t2.write('set style 12\n')

        t.write('match admin white 1 0\n')
        self.expect('Issuing:', t)
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('<12> ', t)
        self.expect('<12> ', t2)

        moves = ['Nf3', 'Nf6', 'Ng1', 'Ng8', 'Nf3', 'Nf6',
            'Ng1', 'Ng8']

        wtm = True
        for mv in moves:
            if wtm:
                #print 'sending %s to white' % mv.text
                t.write('%s\n' % mv)
            else:
                #print 'sending %s to black' % mv.text
                t2.write('%s\n' % mv)
            self.expect('<12> ', t)
            self.expect('<12> ', t2)
            wtm = not wtm

        t.write('draw\n')
        self.expect('{Game 1 (GuestABCD vs. admin) Game drawn by repetition} 1/2-1/2', t)
        self.expect('{Game 1 (GuestABCD vs. admin) Game drawn by repetition} 1/2-1/2', t2)

        self.close(t)
        self.close(t2)

    def test_draw_repetition_claim_later(self):
        t = self.connect_as_guest('GuestABCD')
        t2 = self.connect_as_admin()

        t.write('set style 12\n')
        t2.write('set style 12\n')

        t.write('match admin white 1 0\n')
        self.expect('Issuing:', t)
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('<12> ', t)
        self.expect('<12> ', t2)

        moves = ['Nf3', 'Nf6', 'd3', 'Nc6', 'Nc3', 'Nb8', 'Nb1', 'Nc6',
            'Nc3', 'Nb8', 'Nb1', 'Ne4']

        wtm = True
        for mv in moves:
            if wtm:
                t.write('%s\n' % mv)
            else:
                t2.write('%s\n' % mv)
            self.expect('<12> ', t)
            self.expect('<12> ', t2)
            wtm = not wtm

        # Old fics allows either white or black to claim a draw here.
        # We only allow white to claim a draw; black should have
        # claimed it before he or she moved.
        t.write('draw\n')
        self.expect('{Game 1 (GuestABCD vs. admin) Game drawn by repetition} 1/2-1/2', t)
        self.expect('{Game 1 (GuestABCD vs. admin) Game drawn by repetition} 1/2-1/2', t2)

        t2.write('aclearhist admin\n')
        self.expect('History of admin cleared.', t2)

        self.close(t)
        self.close(t2)

    def test_draw_repetition_claim_too_late(self):
        t = self.connect_as_guest('GuestABCD')
        t2 = self.connect_as_admin()

        t.write('set style 12\n')
        t2.write('set style 12\n')

        t.write('match admin white 1 0\n')
        self.expect('Issuing:', t)
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('<12> ', t)
        self.expect('<12> ', t2)

        moves = ['Nf3', 'Nf6', 'd3', 'Nc6', 'Nc3', 'Nb8', 'Nb1', 'Nc6',
            'Nc3', 'Nb8', 'Nb1', 'Ne4']

        wtm = True
        for mv in moves:
            if wtm:
                t.write('%s\n' % mv)
            else:
                t2.write('%s\n' % mv)
            self.expect('<12> ', t)
            self.expect('<12> ', t2)
            wtm = not wtm

        t2.write('draw\n')
        # see note in test_draw_repetition_claim_later()
        self.expect('Offering a draw', t2)
        self.expect_not('drawn by repetition', t)

        t.write('abort\n')
        t2.write('abort\n')

        self.close(t)
        self.close(t2)

    def test_examine_commands(self):
        t = self.connect_as_guest()
        t2 = self.connect_as_admin()

        t.write('match admin white 1 0\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('Creating: ', t)
        self.expect('Creating: ', t2)

        t.write('ex\n')
        self.expect('You are playing a game.', t)

        t.write('forward\n')
        self.expect('You are not examining a game.', t)

        t.write('back\n')
        self.expect('You are not examining a game.', t)

        t.write('unex\n')
        self.expect('You are not examining a game.', t)

        t.write('abort\n')
        self.expect('aborted on move 1', t2)

        self.close(t)
        self.close(t2)

class TestResign(Test):
    def test_resign_white(self):
        t = self.connect_as_guest('GuestABCD')
        t2 = self.connect_as_admin()

        t.write('match admin white 1 0\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('Creating: ', t)
        self.expect('Creating: ', t2)

        t.write('resign\n')
        self.expect('{Game 1 (GuestABCD vs. admin) GuestABCD resigns} 0-1', t)
        self.expect('{Game 1 (GuestABCD vs. admin) GuestABCD resigns} 0-1', t2)

        t2.write('aclearhist admin\n')
        self.expect('History of admin cleared.', t2)
        self.close(t)
        self.close(t2)

    def test_resign_black(self):
        t = self.connect_as_guest('GuestABCD')
        t2 = self.connect_as_admin()

        t.write('match admin white 1 0\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('Creating: ', t)
        self.expect('Creating: ', t2)

        t2.write('resign\n')
        self.expect('{Game 1 (GuestABCD vs. admin) admin resigns} 1-0', t)
        self.expect('{Game 1 (GuestABCD vs. admin) admin resigns} 1-0', t2)

        t2.write('aclearhist admin\n')
        self.expect('History of admin cleared.', t2)
        self.close(t)
        self.close(t2)

class TestRefresh(Test):
    def test_refresh(self):
        t = self.connect_as_guest('GuestABCD')
        t2 = self.connect_as_admin()
        t.write('set style 12\n')
        t2.write('set style 12\n')

        t.write('match admin white 7 9\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('Creating: ', t)
        self.expect('Creating: ', t2)

        self.expect('<12> rnbqkbnr pppppppp -------- -------- -------- -------- PPPPPPPP RNBQKBNR W -1 1 1 1 1 0 1 GuestABCD admin 1 7 9 39 39 420 420 1 none (0:00) none 0 0 0', t)
        self.expect('<12> ', t2)

        t.write('refresh\n')
        self.expect('<12> ', t)
        self.expect_not('<12> ', t2)

        t3 = self.connect_as_guest('GuestDEFG')
        t3.write('set style 12\n')
        t3.write('re\n')
        self.expect('You are not playing, examining, or observing', t3)
        t3.write('re 999\n')
        self.expect('There is no such game', t3)
        t3.write('re 1\n')
        self.expect('<12> rnbqkbnr pppppppp -------- -------- -------- -------- PPPPPPPP RNBQKBNR W -1 1 1 1 1 0 1 GuestABCD admin -3 7 9 39 39 420 420 1 none (0:00) none 0 0 0', t3)
        t3.write('re nosuchuser\n')
        self.expect('No player named "nosuchuser" is online', t3)
        t3.write('re admi\n')
        self.expect('<12> rnbqkbnr pppppppp -------- -------- -------- -------- PPPPPPPP RNBQKBNR W -1 1 1 1 1 0 1 GuestABCD admin -3 7 9 39 39 420 420 1 none (0:00) none 0 0 0', t3)

        t3.write('o 1\n')
        self.expect('<12> ', t3)
        t3.write('REF GUESTDEF\n')
        self.expect('GuestDEFG is not playing or examining', t3)
        t3.write('ref\n')
        self.expect('<12> rnbqkbnr pppppppp -------- -------- -------- -------- PPPPPPPP RNBQKBNR W -1 1 1 1 1 0 1 GuestABCD admin 0 7 9 39 39 420 420 1 none (0:00) none 0 0 0', t3)
        self.close(t3)

        self.close(t)
        self.close(t2)

class TestMoves(Test):
    def test_moves_played(self):
        t = self.connect_as_guest('GuestABCD')
        t2 = self.connect_as_admin()
        t.write('set style 12\n')
        t.write('iset ms 1\n')
        t2.write('set style 12\n')
        t2.write('iset ms 1\n')

        t2.write('moves\n')
        self.expect('You are not playing, examining, or observing a game', t2)

        t2.write('moves 1\n')
        self.expect('There is no such game', t2)

        t2.write('moves nosuchuser\n')
        self.expect('No player named "nosuchuser" is online', t2)

        t.write('match admin white 1 0\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')

        self.expect('<12> ', t)
        self.expect('<12> ', t2)

        t.write('e4\n')
        self.expect('<12> ', t)
        self.expect('<12> ', t2)

        t.write('moves\n')
        self.expect('Movelist for game 1:\r\n\r\nGuestABCD (++++) vs. admin (----) --- ', t)
        self.expect('''Move  GuestABCD               admin\r\n----  ---------------------   ---------------------\r\n  1.  e4      (0:00.000)      \r\n      {Still in progress} *''', t)

        t2.write('c5\n')
        self.expect('<12> ', t)
        self.expect('<12> ', t2)

        t2.write('moves\n')
        self.expect('''Move  GuestABCD               admin\r\n----  ---------------------   ---------------------\r\n  1.  e4      (0:00.000)      c5      (0:00.000)\r\n      {Still in progress} *''', t2)

        t3 = self.connect_as_guest()
        t3.write('set style 12\n')
        t3.write('iset ms 1\n')
        t3.write('moves 1\n')
        self.expect('''Move  GuestABCD               admin\r\n----  ---------------------   ---------------------\r\n  1.  e4      (0:00.000)      c5      (0:00.000)\r\n      {Still in progress} *''', t3)
        t3.write('moves admi\n')
        self.expect('''Move  GuestABCD               admin\r\n----  ---------------------   ---------------------\r\n  1.  e4      (0:00.000)      c5      (0:00.000)\r\n      {Still in progress} *''', t3)
        t3.write('moves\n')
        self.expect('You are not playing, examining, or observing a game', t3)
        t3.write('o 1\n')
        t3.write('moves\n')
        self.expect('''Move  GuestABCD               admin\r\n----  ---------------------   ---------------------\r\n  1.  e4      (0:00.000)      c5      (0:00.000)\r\n      {Still in progress} *''', t3)
        self.close(t3)

        t.write('abo\n')
        t2.write('abo\n')
        self.expect('aborted by agreement', t)

        self.close(t)
        self.close(t2)

    def test_moves_examined(self):
        t = self.connect_as_guest('GuestABCD')
        t.write('ex\n')
        self.expect('Starting a game', t)
        t.write('d4\n')
        self.expect('GuestABCD moves: d4', t)
        t.write('d5\n')
        self.expect('GuestABCD moves: d5', t)
        t.write('c4\n')
        self.expect('GuestABCD moves: c4', t)

        t.write('moves\n')
        self.expect('Movelist for game 1:\r\n\r\nGuestABCD (++++) vs. GuestABCD (++++) --- ', t)
        self.expect('''Move  GuestABCD               GuestABCD\r\n----  ---------------------   ---------------------\r\n''', t)
        self.expect('''  1.  d4      (0:00)          d5      (0:00)\r\n''', t)
        self.expect('''  2.  c4      (0:00)''', t)
        self.expect('''      {Still in progress} *''', t)

        t.write('unex\n')

        self.close(t)

class TestGames(Test):
    def test_games(self):
        t = self.connect_as_guest('GuestABCD')
        t2 = self.connect_as_admin()

        t.write('games\n')
        self.expect('There are no games in progress', t)

        t.write('match admin white 1 0\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('Creating: GuestABCD (++++) admin (----) unrated lightning 1 0', t)
        self.expect('Creating: GuestABCD (++++) admin (----) unrated lightning 1 0', t2)

        t.write('games\n')
        #self.expect('')
        t.write('abort\n')
        t2.write('abort\n')

        self.close(t)
        self.close(t2)

class TestDisconnect(Test):
    def test_forfeit_disconnection_quit(self):
        t = self.connect_as_guest('GuestABCD')
        t2 = self.connect_as_admin()

        t.write('match admin white 1 0\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('Creating: ', t)
        self.expect('Creating: ', t2)

        t.close()
        self.expect('{Game 1 (GuestABCD vs. admin) GuestABCD forfeits by disconnection} 0-1', t2)

        t2.write('aclearhist admin\n')
        self.expect('History of admin cleared.', t2)
        self.close(t2)

    def test_forfeit_disconnection_quit(self):
        t = self.connect_as_guest('GuestABCD')
        t2 = self.connect_as_admin()

        t.write('match admin white 1 0\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('Creating: ', t)
        self.expect('Creating: ', t2)

        t.write('quit\n')
        self.expect('{Game 1 (GuestABCD vs. admin) GuestABCD forfeits by disconnection} 0-1', t)
        self.expect('{Game 1 (GuestABCD vs. admin) GuestABCD forfeits by disconnection} 0-1', t2)

        t.close()
        t2.write('aclearhist admin\n')
        self.expect('History of admin cleared.', t2)
        self.close(t2)

    def test_abort_disconnection(self):
        t = self.connect_as_guest('GuestABCD')
        t2 = self.connect_as_admin()

        t.write('match admin white 1 0\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('Creating: ', t)
        self.expect('Creating: ', t2)

        t2.write('quit\n')
        self.expect('{Game 1 (GuestABCD vs. admin) admin aborts by disconnection} *', t)
        self.expect('{Game 1 (GuestABCD vs. admin) admin aborts by disconnection} *', t2)
        t2.close()
        self.close(t)

class TestMoretime(Test):
    @with_player('TestPlayer')
    def test_moretime(self):
        t = self.connect_as_admin()
        t2 = self.connect_as('testplayer')
        t3 = self.connect_as_guest()

        t.write('set style 12\n')
        t2.write('set style 12\n')
        t3.write('set style 12\n')

        t.write('match testp white 6+10\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('Creating: ', t)
        self.expect('Creating: ', t2)

        t3.write('o admin\n')
        self.expect('admin (----) TestPlayer (----)', t3)

        self.expect('<12> rnbqkbnr pppppppp -------- -------- -------- -------- PPPPPPPP RNBQKBNR W -1 1 1 1 1 0 1 admin TestPlayer 1 6 10 39 39 360 360 1 none (0:00) none 0 0 0', t)
        self.expect('<12> rnbqkbnr pppppppp -------- -------- -------- -------- PPPPPPPP RNBQKBNR W -1 1 1 1 1 0 1 admin TestPlayer -1 6 10 39 39 360 360 1 none (0:00) none 1 0 0', t2)
        self.expect('<12> rnbqkbnr pppppppp -------- -------- -------- -------- PPPPPPPP RNBQKBNR W -1 1 1 1 1 0 1 admin TestPlayer 0 6 10 39 39 360 360 1 none (0:00) none 0 0 0', t3)

        t.write('moretime 40\n')
        self.expect("You have added 40 seconds to TestPlayer's clock.", t)
        self.expect("admin has added 40 seconds to your clock.", t2)
        self.expect("admin has added 40 seconds to TestPlayer's clock.", t3)

        self.expect('<12> rnbqkbnr pppppppp -------- -------- -------- -------- PPPPPPPP RNBQKBNR W -1 1 1 1 1 0 1 admin TestPlayer 1 6 10 39 39 360 400 1 none (0:00) none 0 0 0', t)
        self.expect('<12> rnbqkbnr pppppppp -------- -------- -------- -------- PPPPPPPP RNBQKBNR W -1 1 1 1 1 0 1 admin TestPlayer -1 6 10 39 39 360 400 1 none (0:00) none 1 0 0', t2)
        self.expect('<12> rnbqkbnr pppppppp -------- -------- -------- -------- PPPPPPPP RNBQKBNR W -1 1 1 1 1 0 1 admin TestPlayer 0 6 10 39 39 360 400 1 none (0:00) none 0 0 0', t3)

        t2.write('moretime 5\n')
        self.expect("You have added 5 seconds to admin's clock.", t2)
        self.expect("TestPlayer has added 5 seconds to your clock.", t)
        self.expect("TestPlayer has added 5 seconds to admin's clock.", t3)

        self.expect('<12> rnbqkbnr pppppppp -------- -------- -------- -------- PPPPPPPP RNBQKBNR W -1 1 1 1 1 0 1 admin TestPlayer 1 6 10 39 39 365 400 1 none (0:00) none 0 0 0', t)
        self.expect('<12> rnbqkbnr pppppppp -------- -------- -------- -------- PPPPPPPP RNBQKBNR W -1 1 1 1 1 0 1 admin TestPlayer -1 6 10 39 39 365 400 1 none (0:00) none 1 0 0', t2)
        self.expect('<12> rnbqkbnr pppppppp -------- -------- -------- -------- PPPPPPPP RNBQKBNR W -1 1 1 1 1 0 1 admin TestPlayer 0 6 10 39 39 365 400 1 none (0:00) none 0 0 0', t3)

        t.write('moretime 40000\n')
        self.expect('Invalid number of seconds.', t)
        t.write('moretime 0\n')
        self.expect('Invalid number of seconds.', t)
        t3.write('moretime 5\n')
        self.expect('You are not playing a game.', t3)

        t.write('abo\n')
        self.expect('aborted on move 1', t3)

        self.close(t)
        self.close(t2)
        self.close(t3)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
