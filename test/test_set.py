from test import *

class TestSet(Test):
    def test_set(self):
        t = self.connect_as_guest()

        # abbreviated var
        t.write("set te 0\n")
        self.expect("You will not hear direct tells from unregistered", t)

        t.write('set t 1\n')
        self.expect("Ambiguous variable", t)

        t.write("set formula\n")
        self.expect("formula unset", t)
        
        t.write("set shout off\n")
        self.expect("You will not hear shouts", t)
        t.write("set shout ON\n")
        self.expect("You will now hear shouts", t)

        self.close(t)

    def test_bad_set(self):
        t = self.connect_as_guest()
        t.write('set too bar\n')
        self.expect("No such variable", t)
        t.write('set shout bar\n')
        self.expect("Bad value given", t)
        self.close(t)

    def test_toggle(self):
        t = self.connect_as_guest()
        t.write('set tell 1\n')
        self.expect("You will now hear", t)
        t.write('set tell\n')
        self.expect("You will not hear", t)
        t.write('set tell\n')
        self.expect("You will now hear", t)
        self.close(t)

    def test_set_persistence(self):
        t = self.connect_as_admin()
        t.write('set shout 0\n')
        t.write('vars\n')
        self.expect('shout=0', t)
        self.close(t)

        t = self.connect_as_admin()
        t.write('vars\n')
        self.expect('shout=0', t)
        t.write('set shout 1\n')
        self.close(t)

        t = self.connect_as_admin()
        t.write('vars\n')
        self.expect('shout=1', t)
        self.close(t)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
