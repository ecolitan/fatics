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

timeseal_prog = '../timeseal/openseal'
wine_prog = '/usr/bin/wine'
timeseal_prog_win = '/home/wmahan/chess/timeseal.exe'

class TestTimeseal(Test):
    def test_timeseal(self):
        if not os.path.exists(timeseal_prog):
            raise unittest.SkipTest('no timeseal binary')

        try:
            import pexpect
        except ImportError:
            raise unittest.SkipTest('pexpect module not installed')

        process = pexpect.spawn(timeseal_prog, [host, str(port)])

        process.expect_exact('login:')
        process.send('admin\n')
        process.send('%s\n' % admin_passwd)

        process.expect_exact('fics%')

        process.send('finger\n')
        process.expect_exact('Finger of admin')
        process.expect_exact('Timeseal:    On')

        process.send('quit\n')
        process.expect_exact('Thank you for using')
        process.expect_exact(pexpect.EOF)
        process.close()

class TestTimesealWindows(Test):
    def test_timeseal_windows(self):
        if not os.path.exists(wine_prog):
            raise unittest.SkipTest('no wine binary')
        if not os.path.exists(timeseal_prog_win):
            raise unittest.SkipTest('no timeseal windows binary')

        try:
            import pexpect
        except ImportError:
            raise unittest.SkipTest('pexpect module not installed')

        process = pexpect.spawn(wine_prog,
            [timeseal_prog_win, host, str(port)])

        process.expect_exact('login:')
        process.send('admin\n')
        process.send('%s\n' % admin_passwd)
        process.expect_exact('fics%')

        process.send('finger\n')
        process.expect_exact('Finger of admin')
        process.expect_exact('Timeseal:    On')

        process.send('quit\n')
        process.expect_exact('Thank you for using')
        process.expect_exact(pexpect.EOF)
        process.close()

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
