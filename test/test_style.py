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

class TestStyle1(Test):
    @with_player('testplayer', 'testpass')
    def test_style1(self):
        t = self.connect_as('testplayer', 'testpass')
        t2 = self.connect_as_admin()
        t.write('set style 1\n')
        t.write('iset ms 1\n')
        t2.write('set style 1\n')

        t.write('match admin white 1 0 zh\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('Creating: ', t)
        self.expect('Creating: ', t2)

        exp_text = '''
Game 1: testplayer (----) admin (----) rated lightning crazyhouse 1 0

Black holding: []
       ---------------------------------
    8  | *r| *n| *b| *q| *k| *b| *n| *r|     Move # : 1 (White)
       |---+---+---+---+---+---+---+---|
    7  | *p| *p| *p| *p| *p| *p| *p| *p|
       |---+---+---+---+---+---+---+---|
    6  |   |   |   |   |   |   |   |   |
       |---+---+---+---+---+---+---+---|
    5  |   |   |   |   |   |   |   |   |     Black Clock : 1:00.000
       |---+---+---+---+---+---+---+---|
    4  |   |   |   |   |   |   |   |   |     White Clock : 1:00.000
       |---+---+---+---+---+---+---+---|
    3  |   |   |   |   |   |   |   |   |     Black Strength : 24
       |---+---+---+---+---+---+---+---|
    2  | P | P | P | P | P | P | P | P |     White Strength : 24
       |---+---+---+---+---+---+---+---|
    1  | R | N | B | Q | K | B | N | R |
       ---------------------------------
         a   b   c   d   e   f   g   h
White holding: []'''
        for line in exp_text.split('\n'):
            self.expect(line.replace('\n', '\r\n'), t)

        exp_text = '''
Game 1: testplayer (----) admin (----) rated lightning crazyhouse 1 0

White holding: []
       ---------------------------------
    1  | R | N | B | K | Q | B | N | R |     Move # : 1 (White)
       |---+---+---+---+---+---+---+---|
    2  | P | P | P | P | P | P | P | P |
       |---+---+---+---+---+---+---+---|
    3  |   |   |   |   |   |   |   |   |
       |---+---+---+---+---+---+---+---|
    4  |   |   |   |   |   |   |   |   |     Black Clock : 1:00
       |---+---+---+---+---+---+---+---|
    5  |   |   |   |   |   |   |   |   |     White Clock : 1:00
       |---+---+---+---+---+---+---+---|
    6  |   |   |   |   |   |   |   |   |     Black Strength : 24
       |---+---+---+---+---+---+---+---|
    7  | *p| *p| *p| *p| *p| *p| *p| *p|     White Strength : 24
       |---+---+---+---+---+---+---+---|
    8  | *r| *n| *b| *k| *q| *b| *n| *r|
       ---------------------------------
         h   g   f   e   d   c   b   a
Black holding: []'''
        for line in exp_text.split('\n'):
            self.expect(line.replace('\n', '\r\n'), t2)

        t.write('e4\n')

        exp_text = '''
Game 1: testplayer (----) admin (----) rated lightning crazyhouse 1 0

Black holding: []
       ---------------------------------
    8  | *r| *n| *b| *q| *k| *b| *n| *r|     Move # : 1 (Black)
       |---+---+---+---+---+---+---+---|
    7  | *p| *p| *p| *p| *p| *p| *p| *p|
       |---+---+---+---+---+---+---+---|
    6  |   |   |   |   |   |   |   |   |
       |---+---+---+---+---+---+---+---|
    5  |   |   |   |   |   |   |   |   |     Black Clock : 1:00.000
       |---+---+---+---+---+---+---+---|
    4  |   |   |   |   | P |   |   |   |     White Clock : 1:00.000
       |---+---+---+---+---+---+---+---|
    3  |   |   |   |   |   |   |   |   |     Black Strength : 24
       |---+---+---+---+---+---+---+---|
    2  | P | P | P | P |   | P | P | P |     White Strength : 24
       |---+---+---+---+---+---+---+---|
    1  | R | N | B | Q | K | B | N | R |
       ---------------------------------
         a   b   c   d   e   f   g   h
White holding: []'''
        for line in exp_text.split('\n'):
            self.expect(line.replace('\n', '\r\n'), t)

        exp_text = '''
Game 1: testplayer (----) admin (----) rated lightning crazyhouse 1 0

White holding: []
       ---------------------------------
    1  | R | N | B | K | Q | B | N | R |     Move # : 1 (Black)
       |---+---+---+---+---+---+---+---|
    2  | P | P | P |   | P | P | P | P |     White Moves : 'e4      (0:00)'
       |---+---+---+---+---+---+---+---|
    3  |   |   |   |   |   |   |   |   |
       |---+---+---+---+---+---+---+---|
    4  |   |   |   | P |   |   |   |   |     Black Clock : 1:00
       |---+---+---+---+---+---+---+---|
    5  |   |   |   |   |   |   |   |   |     White Clock : 1:00
       |---+---+---+---+---+---+---+---|
    6  |   |   |   |   |   |   |   |   |     Black Strength : 24
       |---+---+---+---+---+---+---+---|
    7  | *p| *p| *p| *p| *p| *p| *p| *p|     White Strength : 24
       |---+---+---+---+---+---+---+---|
    8  | *r| *n| *b| *k| *q| *b| *n| *r|
       ---------------------------------
         h   g   f   e   d   c   b   a
Black holding: []'''
        for line in exp_text.split('\n'):
            self.expect(line.replace('\n', '\r\n'), t2)

        t2.write('d5\n')
        self.expect('d5', t)
        t.write('exd5\n')
        self.expect('Black holding: []', t)
        self.expect('White holding: [P]', t)
        self.expect('White holding: [P]', t2)
        self.expect('Black holding: []', t2)

        t.write('abo\n')
        t2.write('abo\n')
        self.expect('aborted', t)

        self.close(t)
        self.close(t2)

class TestStyle12(Test):
    @with_player('testplayer', 'testpass')
    def test_style12(self):
        t = self.connect_as('testplayer', 'testpass')
        t2 = self.connect_as_admin()
        t.write('set style 12\n')
        t.write('iset ms 1\n')
        t2.write('set style 12\n')

        t.write('match admin white 1 0\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('Creating: ', t)
        self.expect('Creating: ', t2)

        self.expect('\r\n<12> rnbqkbnr pppppppp -------- -------- -------- -------- PPPPPPPP RNBQKBNR W -1 1 1 1 1 0 1 testplayer admin 1 1 0 39 39 60000 60000 1 none (0:00.000) none 0 0 0\r\n', t)
        self.expect('\r\n<12> rnbqkbnr pppppppp -------- -------- -------- -------- PPPPPPPP RNBQKBNR W -1 1 1 1 1 0 1 testplayer admin -1 1 0 39 39 60 60 1 none (0:00) none 1 0 0\r\n', t2)

        t.write('d4\n')

        self.expect('\r\n<12> rnbqkbnr pppppppp -------- -------- ---P---- -------- PPP-PPPP RNBQKBNR B -1 1 1 1 1 0 1 testplayer admin -1 1 0 39 39 60000 60000 1 P/d2-d4 (0:00.000) d4 0 0 0\r\n', t)
        self.expect('\r\n<12> rnbqkbnr pppppppp -------- -------- ---P---- -------- PPP-PPPP RNBQKBNR B -1 1 1 1 1 0 1 testplayer admin 1 1 0 39 39 60 60 1 P/d2-d4 (0:00) d4 1 0 0\r\n', t2)

        t2.write('d5\n')
        #m = self.expect_re(r'\r\n<12> rnbqkbnr ppp-pppp -------- ---p---- ---P---- -------- PPP-PPPP RNBQKBNR W -1 1 1 1 1 0 1 testplayer admin 1 1 0 39 39 (\d+) 60000 2 P/d7-d5 (0:00.000) d5 0 1 0\r\n', t)
        m = self.expect_re(r'\r\n<12> rnbqkbnr ppp-pppp -------- ---p---- ---P---- -------- PPP-PPPP RNBQKBNR W -1 1 1 1 1 0 1 testplayer admin 1 1 0 39 39 (\d+)', t)
        # on slow machines a time may tick away
        # XXX this should really only be done with timeseal
        self.assert_(59990 <= int(m.group(1)) <= 60000)
        self.expect('\r\n<12> rnbqkbnr ppp-pppp -------- ---p---- ---P---- -------- PPP-PPPP RNBQKBNR W -1 1 1 1 1 0 1 testplayer admin -1 1 0 39 39 60 60 2 P/d7-d5 (0:00) d5 1 1 0\r\n', t2)

        self.close(t)
        self.close(t2)

    def test_style12_nowrap(self):
        """ Long style12 lines should not be wrapped. """
        t = self.connect_as_guest('GuestABCDEFGHIJKL')
        t2 = self.connect_as_guest('GuestMNOPQRSTUVWX')
        t.write('set style 12\n')
        t.write('iset ms 1\n')
        t2.write('set style 12\n')
        t2.write('finger\n')

        t.write('match guestmnopqrstuvwx white 1 0\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('Creating: ', t)
        self.expect('Creating: ', t2)

        self.expect('\r\n<12> rnbqkbnr pppppppp -------- -------- -------- -------- PPPPPPPP RNBQKBNR W -1 1 1 1 1 0 1 GuestABCDEFGHIJKL GuestMNOPQRSTUVWX 1 1 0 39 39 60000 60000 1 none (0:00.000) none 0 0 0\r\n', t)
        self.expect('\r\n<12> rnbqkbnr pppppppp -------- -------- -------- -------- PPPPPPPP RNBQKBNR W -1 1 1 1 1 0 1 GuestABCDEFGHIJKL GuestMNOPQRSTUVWX -1 1 0 39 39 60 60 1 none (0:00) none 1 0 0\r\n', t2)

        t.write('abort\n')
        self.expect('aborted', t2)

        self.close(t)
        self.close(t2)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
