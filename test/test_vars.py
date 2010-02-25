from test import *

class TestVars(Test):
	def test_vars(self):
		t = self.connect_as_guest()
                
                t.write("set tell 0\n")
                self.expect("You will not hear direct tells from unregistered", t)
                t.write("set tell 1\n")
                self.expect("You will now hear direct tells from unregistered", t)
                t.write("set shout 0\n")
                self.expect("You will not hear shouts", t)
                t.write("set shout 1\n")
                self.expect("You will now hear shouts", t)

                self.close(t)

# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent ft=python
