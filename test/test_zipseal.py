# -*- coding: utf-8 -*-
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

import os.path
import subprocess
import telnetlib
import subprocess
import time
import pexpect

from test import *

zipseal_prog = '../timeseal/zipseal'
wine_prog = '/usr/bin/wine'
zipseal_prog_win = '../timeseal/win32/zipseal.exe'
zipseal_port = 5001

class TestZipseal(Test):
    def _connect(self, username, passwd):
        if not os.path.exists(zipseal_prog):
            raise unittest.SkipTest('no zipseal binary')
            return
        try:
            import pexpect
        except ImportError:
            raise unittest.SkipTest('pexpect module not installed')

        p = pexpect.spawn(zipseal_prog, [host, str(zipseal_port)])
        p.expect_exact('login:')
        p.send('%s\n%s\n' % (username, passwd))
        p.expect_exact('fics%')

        return p

    def _close(self, t):
        """ Gracefully close a connection. """
        t.send('quit\n')
        t.expect_exact('Thank you for using')
        t.expect_exact(pexpect.EOF)
        t.close()

    def test_zipseal(self):
        process = self._connect('admin', admin_passwd)

        process.send('iset nowrap 1\n')
        process.expect_exact('nowrap set.')

        process.send('fi admin\n')
        process.expect_exact('Finger of admin')
        process.expect_exact('Zipseal:     On')

        process.send('''t admin Les naïfs ægithales hâtifs pondant à Noël où il gèle sont sûrs d'être déçus et de voir leurs drôles d'œufs abîmés.\n''')
        process.expect_exact('''tells you: Les naïfs ægithales hâtifs pondant à Noël où il gèle sont sûrs d'être déçus et de voir leurs drôles d'œufs abîmés''')


        self._close(process)

    def test_zipseal_game(self):
        p1 = self._connect('admin', admin_passwd)
        p2 = self._connect('GuestABCD', '')

        p1.send("set style 12\n")
        p2.send("set style 12\n")
        p1.send('match guestabcd 3+0 black\n')
        p2.expect_exact('Challenge:')
        p2.send('accept\n')
        p1.expect_exact('<12> ')
        p2.expect_exact('<12> ')

        p2.send('d4\n')
        p1.expect_exact('<12> ')
        p2.expect_exact('<12> ')

        p1.send('d5\n')
        p1.expect_exact('<12> ')
        p2.expect_exact('<12> ')

        time.sleep(1)
        p2.send('c4\n')
        p1.expect_exact('<12> ')
        p2.expect_exact('<12> ')

        p2.send('abo\n')
        p1.expect_exact('abort')
        p1.send('abort\n')
        p2.expect_exact('aborted by agreement')

        self._close(p1)
        self._close(p2)

    def test_zipseal_error(self):
        t = telnetlib.Telnet(host, zipseal_port, 120)
        t.write('\n')
        self.expect_EOF(t)
        t.close()

    def test_long_utf8(self):
        t = self._connect('admin', admin_passwd)

        t.send('iset nowrap 1\n')
        t.expect_exact('nowrap set.')

        t.send('t admin Μπορώ να φάω σπασμένα γυαλιά χωρίς να πάθω τίποτα.Μπορώ να φάω σπασμένα γυαλιά χωρίς να πάθω τίποτα.Μπορώ να φάω σπασμένα γυαλιά χωρίς να πάθω τίποτα.Μπορώ να φάω σπασμένα γυαλιά χωρίς να πάθω τίποτα.Μπορώ να φάω σπασμένα γυαλιά χωρίς να πάθω τίποτα.Μπορώ να φάω σπασμένα γυαλιά χωρίς να πάθω τίποτα.\n')
        t.expect_exact('admin(*) tells you: Μπορώ να φάω σπασμένα γυαλιά χωρίς να πάθω τίποτα.Μπορώ να φάω σπασμένα γυαλιά χωρίς να πάθω τίποτα.Μπορώ να φάω σπασμένα γυαλιά χωρίς να πάθω τίποτα.Μπορώ να φάω σπασμένα γυαλιά χωρίς να πάθω τίποτα.Μπορώ να φάω σπασμένα γυαλιά χωρίς να πάθω τίποτα.Μπορώ να φάω σπασμένα γυαλιά χωρίς να πάθω τίποτα.')

        self._close(t)

class TestZipsealWindows(Test):
    def test_zipseal_windows(self):
        if not os.path.exists(wine_prog):
            raise unittest.SkipTest('no wine binary')
        if not os.path.exists(zipseal_prog_win):
            raise unittest.SkipTest('no zipseal windows binary')

        process = pexpect.spawn(wine_prog,
            [zipseal_prog_win, host, str(zipseal_port)])

        process.expect_exact('login:')
        process.send('admin\n')
        process.send('%s\n' % admin_passwd)
        process.expect_exact('fics%')

        process.send('finger\n')
        process.expect_exact('Finger of admin')
        process.expect_exact('Zipseal:     On')
        process.send('t admin В чащах юга жил-был цитрус? Да, но фальшивый экземпляр! ёъ.\n')
        process.expect_exact('admin(*) tells you: В чащах юга жил-был цитрус? Да, но фальшивый экземпляр! ёъ.')

        process.send('quit\n')
        process.expect_exact('Thank you for using')
        process.expect_exact(pexpect.EOF)
        process.close()

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
