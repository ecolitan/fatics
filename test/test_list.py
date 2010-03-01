from test import *

class TestList(Test):
    def test_list(self):
        t = self.connect_as_guest()

        t.write('addlist foo bar\n')
        self.expect("does not match any list", t)

        t.write('sublist foo bar\n')
        self.expect("does not match any list", t)

        t.write('+g admin\n')
        self.expect("You don't have permission", t)

        self.close(t)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
