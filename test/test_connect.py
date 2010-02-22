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
                t.write('\r\n')
                self.expect('login:', t, "blank line at login prompt")

                t.write('ad\r\n')
                self.expect('name should be at least', t, "login username too short")
                
                t.write('adminabcdefghijklmno\r\n')
                self.expect('names may be at most', t, "login username too long")
                
                t.write('admin1\r\n')
                self.expect('names can only consist', t, "login username contains numbers")

                t.write('guest\r\n')
                self.expect('Press return to enter', t, "anonymous guest login start")
                
                t.write('\r\n')
                self.expect(' Starting', t, "anonymous guest login complete")
                self.close(t)

        def testRegisteredUserLogin(self):
                # registered user
                t = self.connect()
                t.write('admin\r\n')
                self.expect('is a registered', t, "registered user login start")

                t.write(admin_passwd + '\r\n')
                self.expect(' Starting', t, "registered user login complete")
                self.close(t)

        def testDoubleLogin(self):
                t = self.connect_as_admin()
                t2 = self.connect()
                t2.write('admin\r\n%s\r\n' % admin_passwd)
                self.expect(' is already logged in', t2)
                self.expect(' has arrived', t)
                t.close()
                t2.close()


class PromptTest(Test):
        def testPrompt(self):
                t = self.connect()
                t.write('guest\r\n\r\n')
                self.expect('fics%', t, "fics% prompt")
                self.close(t)

class TimeoutTest(Test):
        def testTimeout(self):
                t = self.connect()
                self.expect('TIMEOUT', t, "login timeout", timeout=65)
                t.close()
        
        def testGuestTimeoutPassword(self):     
                t = self.connect()
                t.write("guest\r\n")
                self.expect('TIMEOUT', t, "login timeout at password prompt", timeout=65)
                t.close()
                
        """def testGuestTimeout(self):     
                t = self.connect()
                t.write("guest\r\n")
                self.expect('TIMEOUT', t, "login timeout guest", timeout=65)
                t.close()"""

# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent ft=python
