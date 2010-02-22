import os.path
import subprocess
import telnetlib
import subprocess
import time

from test import *
        
timeseal_prog = '/home/wmahan/bin/timeseal'

class TestTimeseal(Test):
	def test_timeseal(self):
                if not os.path.exists(timeseal_prog):
                        # XXX unittest does not support skipping till
                        # python 2.7
                        #self.skip()
                        return
                process = subprocess.Popen([timeseal_prog, host, port], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
                process.stdin.write('admin\n')
                process.stdin.write('%s\n' % admin_passwd)
                process.stdin.write('finger\n')
                process.stdin.write('quit\n')
                time.sleep(1)
                [out, err] = process.communicate()
                self.assert_('fics%' in out)
                self.assert_('Finger of admin' in out)
                self.assert_('Thank you for using' in out)

# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent ft=python
