from test.test import *

class TestCrazyhouse(Test):
    def test_crazyhouse(self):
        moves = ['e4', 'e6', 'Nc3', 'd6', 'd4', 'Nf6', 'Nf3', 'Nc6', 'Bg5', 'Be7', 'Bd3', 'h6', 'Bxf6', 'Bxf6', 'N@h5', 'B@g4', 'Nxf6+', 'Qxf6', 'B@h4', 'Qg6', 'e5', 'Bxf3', 'Bxg6', 'fxg6', 'Qxf3', 'B@e7', 'Q@f7+', 'Kd7', 'd5', 'Nxe5', 'Qxe6+', 'Kd8', 'Qxe7#']
        self._assert_game_is_legal(moves, 'admin checkmated} 1-0')

    def test_crazyhouse_draw(self):
        # Credit for this test game: http://www.tonyjh.com/chess/zh_notes.html
        moves = ['d4', 'd5', 'Bh6', 'Nxh6', 'e4', 'c6', 'Be2', 'B@a6', 'Bxa6', 'Qc7', 'Be2', 'Qd7', 'Ba6', 'Qd8', 'Be2', 'Qd6', 'Ba6', 'Qd8', 'Be2', 'Qd6', 'Ba6', 'Qd8']
        self._assert_game_is_legal(moves, 'drawn by repetition} 1/2-1/2')

    def _assert_game_is_legal(self, moves, result=None):
        t = self.connect_as_user('GuestABCD', '')
        t2 = self.connect_as_admin()
        t.write('set style 12\n')
        t2.write('set style 12\n')

        t.write('match admin white 1 0 crazyhouse\n')
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
            if 'by repetition' in result:
                t2.write('draw\n')
            self.expect(result, t)
            self.expect(result, t2)
        else:
            t.write('abort\n')
            t2.write('abort\n')

        self.close(t)
        self.close(t2)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
