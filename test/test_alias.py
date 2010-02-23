from test import *

class TestAlias(Test):
	def test_alias(self):
		t = self.connect_as_admin()
		t.write('t admin test 1\n')
                self.expect('admin(*) tells you: test 1', t)
		
                t.write('.test 2\n')
                self.expect('admin(*) tells you: test 2', t)

                self.close(t)

# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent ft=python
