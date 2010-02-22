from test import *

class TestFoo(Test):
	def test_foo(self):
		t = self.connect_as_guest()
		t.write('foo\n')
                self.expect("bar", t)
                self.close(t)

# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent ft=python
