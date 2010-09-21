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

from test import *

seal_prog = '../timeseal/zipseal'
wine_prog = '/usr/bin/wine'
seal_prog_win = '../timeseal/win32/zipseal.exe'
zipseal_port = 5001


'''class PexpectMixin(object):
    def _spawn_timeseal(self):
        try:
            import pexpect
        except ImportError:
            self._skip('pexpect module not installed')

        p = pexpect.spawn(seal_prog, [host, str(zipseal_port)])
        return p'''

class TestZipseal(Test):
    def test_zipseal(self):
        if not os.path.exists(seal_prog):
            self._skip('no zipseal binary')
            return
        try:
            import pexpect
        except ImportError:
            self._skip('pexpect module not installed')

        process = pexpect.spawn(seal_prog, [host, str(zipseal_port)])

        process.expect_exact('login:')
        process.send('admin\n')
        process.send('%s\n' % admin_passwd)

        process.expect_exact('fics%')

        process.send('fi admin\n')
        process.expect_exact('Finger of admin')
        process.expect_exact('Zipseal:     On')

        process.send('''t admin Les naïfs ægithales hâtifs pondant à Noël où il gèle sont sûrs d'être déçus et de voir leurs drôles d'œufs abîmés.\n''')
        process.expect_exact('''tells you: Les naïfs ægithales hâtifs pondant à Noël où il gèle sont sûrs d'être déçus et de voir leurs drôles d'œufs abîmés''')

        process.send('quit\n')
        process.expect_exact('Thank you for using')
        process.expect_exact(pexpect.EOF)

        process.close()

class TestZipsealWindows(Test):
    def test_zipseal_windows(self):
        if not os.path.exists(seal_prog_win):
            self._skip('no zipseal windows binary')
            return
        try:
            import pexpect
        except ImportError:
            self._skip('pexpect module not installed')

        process = pexpect.spawn(wine_prog, [seal_prog_win, host, str(zipseal_port)])

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
