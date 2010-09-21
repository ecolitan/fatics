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

seal_prog = '../timeseal/openseal'
seal_prog_win = '/home/wmahan/chess/timeseal.exe'

class TestTimeseal(Test):
    def test_timeseal(self):
        if not os.path.exists(seal_prog):
            self._skip('no timeseal binary')
        process = subprocess.Popen([seal_prog, host, port], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        process.stdin.write('admin\n')
        process.stdin.write('%s\n' % admin_passwd)
        process.stdin.write('finger\n')
        process.stdin.write('quit\n')
        time.sleep(5)
        [out, err] = process.communicate()
        self.assert_('fics%' in out)
        self.assert_('Finger of admin' in out)
        self.assert_('Timeseal:    On\r\n' in out)
        self.assert_('Thank you for using' in out)

class TestTimesealWindows(Test):
    def test_timeseal_windows(self):
        if not os.path.exists(seal_prog_win):
            self._skip('no timeseal windows binary')
            return
        process = subprocess.Popen(['/usr/bin/wine', seal_prog_win, host, port], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

        process.stdin.write('admin\r\n')
        process.stdin.write('%s\r\n' % admin_passwd)
        process.stdin.write('finger\n')
        process.stdin.write('quit\n')
        time.sleep(10)
        [out, err] = process.communicate()
        self.assert_('fics%' in out)
        self.assert_('Finger of admin' in out)
        self.assert_('Timeseal:    On\r\n' in out)
        self.assert_('Thank you for using' in out)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
