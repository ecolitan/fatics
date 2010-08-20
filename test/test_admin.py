from test import *

class CommandTest(Test):
    def test_addplayer(self):
        t = self.connect_as_admin()
        try:
            t.write('addplayer testplayer nobody@example.com Foo Bar\n')
            self.expect('Added:', t)
            t.write('addplayer testplayer nobody@example.com Foo Bar\n')
            self.expect('already registered', t)
        finally:
            t.write('remplayer testplayer\n')
        self.close(t)

    def test_announce(self):
        t = self.connect_as_admin()
        t2 = self.connect_as_guest()

        t.write("announce foo bar baz\n")
        self.expect('(1) **ANNOUNCEMENT** from admin: foo bar baz', t)
        self.expect('**ANNOUNCEMENT** from admin: foo bar baz', t2)
        self.close(t)
        self.close(t2)

    def test_annunreg(self):
        self.adduser('testplayer', 'passwd')
        t = self.connect_as_admin()
        t2 = self.connect_as_guest()
        t3 = self.connect_as_guest()
        t4 = self.connect_as_user('testplayer', 'passwd')

        t.write("annunreg x Y z\n")
        self.expect('(2) **UNREG ANNOUNCEMENT** from admin: x Y z', t)
        self.expect('**UNREG ANNOUNCEMENT** from admin: x Y z', t2)
        self.expect('**UNREG ANNOUNCEMENT** from admin: x Y z', t3)
        self.expect_not('**UNREG ANNOUNCEMENT**', t4)
        self.close(t)
        self.close(t2)
        self.close(t3)
        self.close(t4)

    def test_nuke(self):
        t = self.connect_as_admin()

        t.write('nuke 123\n')
        self.expect('not a valid handle', t)

        t.write('nuke guesttest\n')
        self.expect('no player matching', t)

        t2 = self.connect_as_user('GuestTest', '')
        t.write('nuke guesttest\n')
        self.expect('You have been kicked out', t2)
        self.expect('Nuked: GuestTest', t)
        t2.close()

        t2 = self.connect_as_user('GuestTest', '')
        t.write('asetadmin guesttest 100\n')
        t2.write('nuke admin\n')
        self.expect('need a higher adminlevel', t2)
        self.close(t2)

        self.close(t)

    def test_asetpass(self):
        self.adduser('testplayer', 'passwd')
        t = self.connect_as_admin()

        t2 = self.connect_as_user('GuestTest', '')
        t.write('asetpass GuestTest pass\n')
        self.expect('cannot set the password', t)
        self.close(t2)

        t2 = self.connect_as_user('testplayer', 'passwd')
        t.write('asetpass testplayer test\n')
        self.expect("Password of testplayer changed", t)
        self.expect("admin has changed your password", t2)
        self.close(t)
        self.close(t2)

        t2 = self.connect()
        t2.write('testplayer\ntest\n')
        self.expect('fics%', t2)
        self.close(t2)
        self.deluser('testplayer')


    def test_asetadmin(self):
        self.adduser('testplayer', 'passwd')
        self.adduser('testtwo', 'passwd')
        t = self.connect_as_admin()
        t2 = self.connect_as_user('testplayer', 'passwd')
        t.write('asetadmin testplayer 100\n')
        self.expect('Admin level of testplayer set to 100.', t)
        self.close(t)

        # need to excecute a command before admin commands are
        # recognized.
        self.expect('admin has set your admin level to 100.', t2)
        t2.write('\n')
        t2.write('asetadmin admin 100\n')
        self.expect('You can only set the adminlevel for players below', t2)
        t2.write('asetadmin testplayer 1000\n')
        self.expect('You can only set the adminlevel for players below', t2)

        t2.write('asetadmin testtwo 100\n')
        self.expect('''You can't promote''', t2)

        t2.write('asetadmin testtwo 50\n')
        self.expect('Admin level of testtwo set', t2)
        self.close(t2)
        self.deluser('testplayer')
        self.deluser('testplayer2')

class PermissionsTest(Test):
    def test_permissions(self):
        t = self.connect_as_guest()
        t.write('asetpass admin test\n')
        self.expect('asetpass: Command not found', t)
        self.close(t)


"""not stable
class AreloadTest(Test):
        def runTest(self):
                self.skip()
                t = self.connect()
                t.write('areload\n')
                self.expect('reloaded online', t, "server reload")
                t.close()
"""

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
