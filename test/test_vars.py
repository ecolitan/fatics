from test import *

class TestVars(Test):
	def test_vars(self):
		t = self.connect_as_guest()
		t.write('set t 1\n')
                self.expect("Ambiguous variable", t)
                self.close(t)

# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent ft=python
