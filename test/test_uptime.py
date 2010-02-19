from test import *

class TestDate(Test):
	def test_uptime(self):
		t = self.connect_as_guest()
		t.write('uptime\r\n')
		self.expect('location:', t, "location")
		self.expect('Up for:', t, "uptime")
                t.close()

# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent ft=python
