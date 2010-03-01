from test import *

class TestPassword(Test):
    def test_password(self):
        t = self.connect_as_guest()
        t.write('password foo bar\r\n')
        self.expect("only for registered", t)
        t.close()

        t = self.connect_as_admin()
        t.write('password wrongpass test\r\n')
        self.expect("Incorrect", t)

        t.write('password %s test\r\n' % admin_passwd)
        self.expect("changed", t)
        t.close()

        t = self.connect()
        t.write("admin\r\ntest\r\n")
        self.expect("fics%", t)
        t.write("password test %s\r\n" % admin_passwd)
        t.close()

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
