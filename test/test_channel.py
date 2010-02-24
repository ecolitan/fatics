from test import *

class TestChannel(Test):
	def test_channel_guest(self):
		t = self.connect_as_guest()
               
                # guests should be in 53 by default
                t.write('+ch 53\n')
                self.expect('is already on your channel list', t)
	
                t.write('+ch 1\n')
                self.expect("[1] added to your channel list", t)
               
                t.write('t 1 foo bar baz\n')
                self.expect("(1): foo bar baz", t)
	
                t.write('-ch 1\n')
                self.expect("[1] removed from your channel list", t)
                
                t.write('t 1 foo bar baz\n')
                self.expect("not listening", t)

                self.close(t)
	
        def test_channel_admin(self):
		t = self.connect_as_admin()

                t.write('+ch 100\n')
                self.expect("[100] added to your channel list", t)
                
                t.write('t 100 foo bar baz\n')
                self.expect("(100): foo bar baz", t)
                
                self.close(t)
                
		t = self.connect_as_admin()
                t.write('+ch 100\n')
                self.expect('is already on your channel list', t)
                
                t.write('-ch 100\n')
                self.expect("[100] removed from your channel list", t)
                self.close(t)
                
		t = self.connect_as_admin()
                t.write('-ch 100\n')
                self.expect("is not on your channel list", t)
                self.close(t)

# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent
