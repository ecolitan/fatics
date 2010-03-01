# coding=utf8

import os.path
import subprocess
import telnetlib
import subprocess
import time

from test import *
        
seal_prog = '../timeseal/zipseal'

class TestZipseal(Test):
	def test_zipseal(self):
                if not os.path.exists(seal_prog):
                        # XXX unittest does not support skipping till
                        # python 2.7
                        #self.skip()
                        return
                process = subprocess.Popen([seal_prog, host, port], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
                process.stdin.write('admin\n')
                process.stdin.write('%s\n' % admin_passwd)
                process.stdin.write('fi admin\n')
                process.stdin.write('''t admin Les naïfs ægithales hâtifs pondant à Noël où il gèle sont sûrs d'être déçus et de voir leurs drôles d'œufs abîmés.\n''')
                process.stdin.write('quit\n')
                time.sleep(1)
                [out, err] = process.communicate()
                self.assert_('fics%' in out)
                self.assert_('Finger of admin' in out)
                self.assert_('Zipseal: On' in out)
                self.assert_('''tells you: Les naïfs ægithales hâtifs pondant à Noël où il gèle sont sûrs d'être déçus et de voir leurs drôles d'œufs abîmés''' in out)
                self.assert_('Thank you for using' in out)

# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent
