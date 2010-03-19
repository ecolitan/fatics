from test import *

class TestNotify(Test):
    def test_notify_guest(self):
        t = self.connect_as_guest()
        t.write('+not admin\n')
        self.expect("only registered users", t)

        t2 = self.connect_as_admin()
        t2.write('+not guest\n')
        self.expect("only add registered users", t2)

        self.close(t2)
        self.close(t)

    def test_bad_notify(self):
        t = self.connect_as_admin()
        t.write('+not testplayer\n')
        self.expect("no player matching", t)
        self.close(t)

    def test_notify_user(self):
        self.adduser('TestPlayer', 'test')
        try:
            t = self.connect_as_admin()

            t.write('+notify testplayer\n')
            self.expect("TestPlayer added to your notify list", t)

            t.write('+not testplayer\n')
            self.expect("TestPlayer is already on your notify list", t)

            t2 = self.connect_as_user('testplayer', 'test')
            self.expect("Notification: TestPlayer has arrived", t)

            self.close(t)

            t = self.connect()
            t.write('admin\n%s\n' % admin_passwd)
            self.expect('Present company includes: TestPlayer', t)

            self.close(t2)
            self.expect("Notification: TestPlayer has departed", t)

            t.write('-NOTIFY testplayer\n')
            self.expect('TestPlayer removed from your notify list', t)

            t2 = self.connect_as_user('testplayer', 'test')
            self.expect_not("TestPlayer", t)
            
            self.close(t2)
            self.close(t)
        finally:
            self.deluser('TestPlayer')

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
