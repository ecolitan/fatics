from test import  *

import time

class ConnectTest(OneConnectionTest):
    def test_welcome(self):
        self.expect('Welcome', self.t, "welcome message")

    def test_login(self):
        self.expect('login:', self.t, "login prompt")

class LoginTest(Test):
    def test_login(self):
        t = self.connect()
        t.read_until('login:', 2)
        t.write('\n')
        self.expect('login:', t, "blank line at login prompt")

        t.write('ad\n')
        # login username too short
        self.expect(' should be at least ', t)

        # login username too long
        t.write('adminabcdefghijklmn\n')
        self.expect(' should be at most ', t)

        # login username contains numbers
        t.write('admin1\n')
        self.expect(' should only consist of ', t)

        # anonymous guest login start
        t.write('guest\n')
        self.expect('Press return to enter', t)

        # anonymous guest login complete
        t.write('\n')
        self.expect(' Starting FICS session as ', t)
        self.close(t)

    def test_immediate_disconnect(self):
        t = self.connect()
        t.close()
        # no tests here; we need to make sure this doesn't raise an
        # exception in the server

    """User should not actually be logged in until a correct password
    is entered."""
    def test_half_login(self):
        t = self.connect()
        t.write('admin\n')
        t2 = self.connect_as_guest()
        t2.write('finger admin\n')
        self.expect('Last disconnected:', t2)
        self.close(t2)
        t.close()

    def test_registered_user_login(self):
        t = self.connect()
        # registered login start
        t.write('admin\n')
        self.expect('is a registered', t)

        t.write('not the password\n')
        self.expect('*** Invalid password! ***', t)

        t.write('ADMIN\n')
        self.expect('"admin" is a registered name', t)
        t.write(admin_passwd + '\n')
        self.expect(' Starting FICS session as admin(*)', t)
        self.close(t)

    def test_double_login(self):
        t = self.connect_as_admin()
        t2 = self.connect()
        t2.write('admin\n%s\n' % admin_passwd)
        self.expect(' is already logged in', t2)
        self.expect(' has arrived', t)

        t2.write('fi\n')
        self.expect('On for: ', t2)

        self.close(t)
        self.close(t2)

class PromptTest(Test):
    def test_prompt(self):
        t = self.connect()
        t.write('guest\n\n')
        self.expect('fics%', t, "fics% prompt")
        self.close(t)

class LogoutTest(Test):
    def test_logout(self):
        t = self.connect_as_admin()
        t.write('quit\n')
        self.expect('Thank you for using', t)
        t.close()

    def test_unclean_disconnect(self):
        t = self.connect_as_admin()
        t2 = self.connect_as_guest()
        t2.write('who\n')
        self.expect('2 players', t2)
        t.close()
        time.sleep(0.1)
        t2.write('who\n')
        self.expect('1 player', t2)
        self.close(t2)

""" works but disabled for speed
class TimeoutTest(Test):
    def test_timeout(self):
        t = self.connect()
        self.expect('TIMEOUT', t, "login timeout", timeout=65)
        t.close()

    def test_guest_timeout_password(self):
        t = self.connect()
        t.write("guest\n")
        self.expect('TIMEOUT', t, "login timeout at password prompt", timeout=65)
        t.close()

    def test_guest_timeout(self):
        t = self.connect()
        t.write("guest\n")
        self.expect('TIMEOUT', t, "login timeout guest", timeout=65)
        t.close()
"""

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
