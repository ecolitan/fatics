from test import *

class TestDate(Test):
	def test_date(self):
		t = self.connect_as_guest()
		t.write('date\r\n')
		self.expect('Server time', t, "date")
		self.expect('GMT', t, "date")

# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent ft=python
