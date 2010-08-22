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
            # XXX unittest does not support skipping till
            # python 2.7
            #self.skip()
            return
        process = subprocess.Popen([seal_prog, host, port], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        process.stdin.write('admin\n')
        process.stdin.write('%s\n' % admin_passwd)
        process.stdin.write('finger\n')
        process.stdin.write('quit\n')
        time.sleep(1)
        [out, err] = process.communicate()
        self.assert_('fics%' in out)
        self.assert_('Finger of admin' in out)
        self.assert_('Timeseal:    On\r\n' in out)
        self.assert_('Thank you for using' in out)

class TestTimesealWindows(Test):
    def test_timeseal_windows(self):
        if not os.path.exists(seal_prog_win):
            #self.skip()
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
