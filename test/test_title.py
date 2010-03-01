from test import *

class TestTitle(Test):
    def test_bad_name(self):
        t = self.connect_as_admin()
        t.write('+gm nonexistentname\n')
        self.expect("no player matching", t)
        self.close(t)

    def test_title(self):
        t2 = self.connect_as_guest()
        t2.write('+gm admin\n')
        self.expect("You don't have permission", t2)

        t = self.connect_as_admin()
        t.write('+gm guest\n')
        self.expect('nly registered users may', t)
        self.close(t2)

        t.write('+gm admin\n')
        self.expect("admin added to the GM list", t)

        t.write('t admin a b c\n')
        self.expect("admin(*)(GM) tells you: a b c", t)

        t.write('+gm admin\n')
        self.expect("admin is already in the GM list", t)

        t.write('-gm admin\n')
        self.expect("admin removed from the GM list", t)

        t.write('-gm admin\n')
        self.expect("admin is not in the GM list", t)

        t.write('t admin d e f\n')
        self.expect("admin(*) tells you: d e f", t)

        self.close(t)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
