from test import  *

class ConnectTest(OneConnectionTest):
    def testWelcome(self):
        self.expect('Welcome', self.t, "welcome message")

    def testLogin(self):
        self.expect('login:', self.t, "login prompt")

class LoginTest(Test):
    def testLogin(self):
        t = self.connect()
        t.read_until('login:', 2)
        t.write('\n')
        self.expect('login:', t, "blank line at login prompt")

        t.write('ad\n')
        # login username too short
        self.expect(' should be at least ', t)

        # login username too long
        t.write('adminabcdefghijklmno\n')
        self.expect(' should be at most ', t)

        # login username contains numbers
        t.write('admin1\n')
        self.expect(' should only consist of ', t)

        # anonymous guest login start
        t.write('guest\n')
        self.expect('Press return to enter', t)

        # anonymous guest login complete
        t.write('\n')
        self.expect(' Starting', t)
        self.close(t)

    """User should not actually be logged in until a correct password
    is entered."""
    def testHalfLogin(self):
        t = self.connect()
        t.write('admin\n')
        t2 = self.connect_as_guest()
        t2.write('finger admin\n')
        self.expect('Last disconnected:', t2)
        self.close(t2)
        t.close()

    def testRegisteredUserLogin(self):
        # registered user
        t = self.connect()
        t.write('admin\n')
        self.expect('is a registered', t, "registered user login start")

        t.write(admin_passwd + '\n')
        self.expect(' Starting', t, "registered user login complete")
        self.close(t)

    def testDoubleLogin(self):
        t = self.connect_as_admin()
        t2 = self.connect()
        t2.write('admin\n%s\n' % admin_passwd)
        self.expect(' is already logged in', t2)
        self.expect(' has arrived', t)
        t.close()
        t2.close()


class PromptTest(Test):
    def testPrompt(self):
        t = self.connect()
        t.write('guest\n\n')
        self.expect('fics%', t, "fics% prompt")
        self.close(t)

class TimeoutTest(Test):
    def testTimeout(self):
        t = self.connect()
        self.expect('TIMEOUT', t, "login timeout", timeout=65)
        t.close()

    def testGuestTimeoutPassword(self):
        t = self.connect()
        t.write("guest\n")
        self.expect('TIMEOUT', t, "login timeout at password prompt", timeout=65)
        t.close()

    """
    works but disabled for speed
    def testGuestTimeout(self):
            t = self.connect()
            t.write("guest\n")
            self.expect('TIMEOUT', t, "login timeout guest", timeout=65)
            t.close()"""

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
