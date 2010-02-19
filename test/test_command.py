from test import *

class TestCommand(Test):
	def test_command(self):
		t = self.connect_as_guest()
		t.write('badcommand\r\n')
                self.expect('Command not found', t)

                # abbreviate command
                t.write('fin\r\n')
                self.expect('Finger of ', t)
                
                # don't update idle time
                t.write('$$finger\r\n')
                self.expect('Finger of ', t)

                t.close()

# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent ft=python
