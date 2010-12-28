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

class TestVarsCommand(Test):
    def test_self_vars(self):
        t = self.connect_as_admin()
        t.write('vars\n')
        self.expect('Variable settings of admin:', t)
        self.expect('shout=1', t)
        self.close(t)

    def test_self_vars_guest(self):
        t = self.connect_as_guest('GuestABCD')
        t2 = self.connect_as_guest('GuestEFGH')

        t.write('set prompt ics>\n')
        self.expect('prompt set', t)
        t.write('set interface Test interface\n')
        self.expect('interface set', t)
        t.write('set bugopen 1\n')
        self.expect('now open for bughouse', t)
        t2.write('part guestabcd\n')
        self.expect('offers', t)
        t.write('part guestefgh\n')
        self.expect('agree', t)
        # TODO: follow

        t.write('vars\n')
        self.expect('Variable settings of Guest', t)
        self.expect('shout=1', t)
        self.expect('Prompt: ics>', t)
        self.expect('Interface: Test interface', t)
        self.expect('Bughouse partner: GuestEFGH', t)

        self.close(t)

    def test_other_vars(self):
        t = self.connect_as_admin()
        t2 = self.connect_as_guest()

        t.write('set shout 0\n')
        self.expect('You will not hear shouts.', t)
        t2.write('vars admin\n')
        self.expect('Variable settings of admin:', t2)
        self.expect('shout=0', t2)

        t.write('set shout\n')
        self.expect('You will now hear shouts.', t)
        self.close(t)
        self.close(t2)

    def test_vars_offline(self):
        t = self.connect_as_guest()
        t.write('vars admin\n')
        self.expect('Variable settings of admin:', t)
        self.expect('shout=1', t)
        self.close(t)

    def test_self_ivars(self):
        t = self.connect_as_admin()
        t.write('ivars\n')
        self.expect('Interface variable settings of admin:', t)
        self.expect('smartmove=0', t)
        self.close(t)

    def test_other_ivars(self):
        t = self.connect_as_guest()
        t2 = self.connect_as_admin()
        t.write('ivars admin\n')
        self.expect('Interface variable settings of admin:', t)
        self.expect('smartmove=0', t)
        self.close(t)
        self.close(t2)

    def test_ivars_offline(self):
        t = self.connect_as_guest()
        t.write('ivars admin\n')
        self.expect('No player named "admin" is online.', t)
        self.close(t)

class TestVars(Test):
    def test_vars(self):
        t = self.connect_as_guest()

        t.write("set tell 0\n")
        self.expect("You will not hear direct tells from unregistered", t)
        t.write("set tell 1\n")
        self.expect("You will now hear direct tells from unregistered", t)
        t.write("set shout 0\n")
        self.expect("You will not hear shouts", t)
        t.write("set shout 1\n")
        self.expect("You will now hear shouts", t)
        t.write("set mailmess 1\n")
        self.expect("Your messages will be mailed to you.", t)
        t.write("set mailmess 0\n")
        self.expect("Your messages will not be mailed to you.", t)

        t.write("set open 0\n")
        self.expect("no longer open to receive match requests", t)
        t.write("set open 1\n")
        self.expect("are now open to receive match requests", t)
        t.write("set open 2\n")
        self.expect('Bad value given for variable "open"', t)

        t.write("set style -1\n")
        self.expect('Bad value given for variable "style"', t)

        t.write("set lang Klingon\n")
        self.expect('Bad value given for variable "lang"', t)

        t.write("set style 100\n")
        self.expect('Bad value given for variable "style"', t)

        self.close(t)

    def test_prompt(self):
        t = self.connect_as_guest()
        t.write('set prompt foobar%\n')
        self.expect('prompt set to "foobar% ".', t)

        t.write('fi\n')
        self.expect('Finger of Guest', t)
        self.expect('foobar% ', t)
        self.close(t)

    def test_transient_var_user(self):
        t = self.connect_as_admin()
        t.write('set interface Thief 1.23 Midget edition\n')
        self.expect('interface set to "Thief 1.23 Midget edition"', t)
        self.close(t)

class TestIvars(Test):
    def test_ivars(self):
        t = self.connect_as_guest()

        t.write("iset smartmove 1\n")
        self.expect("smartmove set", t)

        t.write("iset smartmove 0\n")
        self.expect("smartmove unset", t)

        t.write("iset se 1\n")
        self.expect('Ambiguous ivariable "se". Matches: ', t)

        self.close(t)

    def test_login_ivars(self):
        t = self.connect()
        t.write('%b10011101010001000100001000000001000\n')
        self.expect("Ivars set.", t)
        t.write('g\n\n')
        self.expect('fics% ', t)
        t.write('ivar\n')
        self.expect('block=0', t)
        t.close()

    def test_ms(self):
        t = self.connect_as_guest()
        t2 = self.connect_as_admin()
        t.write('match admin white 1 0\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('<12> ', t)
        self.expect('<12> ', t2)

        t3 = self.connect_as_guest()
        t3.write('iset ms 0\n')
        self.expect('ms unset', t3)
        t3.write('ref 1\n')
        self.expect('(0:00)', t3)
        self.expect_not('(0:00.000)', t3)
        t3.write('iset ms 1\n')
        self.expect('ms set', t3)
        t3.write('ref 1\n')
        self.expect('(0:00.000)', t3)
        self.expect_not('(0:00)', t3)
        self.close(t3)

        t.write('abort\n')
        t2.write('abort\n')
        self.close(t)
        self.close(t2)

class TestGameinfo(Test):
    def test_gameinfo(self):
        t = self.connect_as_guest()
        t2 = self.connect_as_admin()
        t.write("match admin 2 12 u white\n")
        t.write('iset gamei 1\n')
        self.expect('gameinfo set.', t)
        self.expect("Challenge:", t2)
        t2.write('a\n')

        self.expect('<g1> 1 p=0 t=chess r=0 u=1,0 it=120,12 i=120,12 pt=0 rt=0,0 ts=0,0 m=2 n=0', t)

        # <g1> 482 p=0 t=blitz r=1 u=0,0 it=180,0 i=180,0 pt=0 rt=2009,2013 ts=1,1 m=2 n=0
        t3 = self.connect_as_guest()
        t3.write('iset gameinfo 1\n')
        t3.write('o 1\n')
        self.expect('<g1> 1 p=0 t=chess r=0 u=1,0 it=120,12 i=120,12 pt=0 rt=0,0 ts=0,0 m=2 n=0', t3)
        self.close(t3)

        t.write('abort\n')

        self.close(t)
        self.close(t2)

# <d1> 314 5 e3 e2e3 100 59800 563
class TestCompressMove(Test):
    def test_compressmove(self):
        t = self.connect_as_guest('GuestABCD')
        t2 = self.connect_as_admin()
        t.write("match admin 2 12 u white\n")
        t.write('set style 12\n')
        t.write('iset compressmove 1\n')
        self.expect('compressmove set.', t)
        self.expect("Challenge:", t2)
        t2.write('a\n')
        self.expect('\r\n<12> rnbqkbnr pppppppp -------- -------- -------- -------- PPPPPPPP RNBQKBNR W -1 1 1 1 1 0 1 GuestABCD admin 1 2 12 39 39 120 120 1 none (0:00) none 0 0 0\r\n', t)
        n = 1

        t.write('e4\n')
        self.expect('<d1> %d 1 e4 e2e4 0 120000 0\r\n' % n, t)
        t2.write('d5\n')
        self.expect('<d1> %d 2 d5 d7d5 0 120000 0\r\n' % n, t)

        t.write('abort\n')
        t2.write('abort\n')
        self.expect('aborted by agreement', t)

        self.close(t)
        self.close(t2)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
