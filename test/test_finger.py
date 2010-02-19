from test import  *

class FingerTest(Test):
        def testFinger(self):
                t = self.connect_as_admin()
                t.write('finger\r\n')
                self.expect('Finger of admin(*):', t, "finger")
                self.expect('On for:', t, "finger of online user")
                
                t.write('finger \r\n')
                self.expect('Finger of admin(*):', t, "finger with trailing space")

                t.write('finger admin\r\n')
                self.expect('Finger of admin(*):', t, "finger with parameter")
                
                t.write('finger ad\r\n')
                self.expect('Finger of admin(*):', t, "finger with prefix")

                t.write('addplayer admintwo nobody@example.com Admin Two\r\n')
                t.write('asetpass admintwo admintwo\r\n')
                t.write('finger ad\r\n')
                self.expect('Finger of admin(*):', t, "finger with prefix ignores offline user")
                t2 = connect()
                t2.write('admintwo\r\nadmintwo\r\n')
                t2.read_until('fics%', 2)
                t2.write('finger ad\r\n')
                self.expect('Matches: admin admintwo', t2, "finger ambiguous online users")
                t2.close()

                t.write('finger notarealuser\r\n')
                self.expect('no player matching', t, "nonexistent user")
                
                t.write('finger admin1\r\n')
                self.expect('not a valid handle', t, "invalid name")
                
                t.write('remplayer admintwo\r\n')
                t.read_until('removed', 2)

                t.close()
        
        def testFingerGuest(self):      
                t = self.connect_as_guest()

                t.write('finger\r\n')
                self.expect('Finger of Guest', t, "finger offline user")

                t.write('finger admin\r\n')
                self.expect('Last disconnected:', t, "finger offline user")
                
                t.write('finger admi\r\n')
                self.expect('Last disconnected:', t, "finger offline user prefix")
                
                t.close()


# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent ft=python
