from test import  *

class FingerTest(Test):
        def test_finger(self):
                t = self.connect_as_admin()
                t.write('finger\r\n')
                self.expect('Finger of admin(*):', t, "finger")
                self.expect('On for:', t, "finger of online user")
                
                # finger with trailing space
                t.write('finger \r\n')
                self.expect('Finger of admin(*):', t)

                # finger with parameter
                t.write('finger admin\r\n')
                self.expect('Finger of admin(*):', t)
                
                # finger with prefix
                t.write('finger ad\r\n')
                self.expect('Finger of admin(*):', t)
                
                t.write('finger a\r\n')
                self.expect('need to specify at least', t)
                
                t.write('finger notarealuser\r\n')
                self.expect('no player matching', t, "nonexistent user")
                
                t.write('finger admin1\r\n')
                self.expect('not a valid handle', t, "invalid name")

                self.close(t)

        def test_ambiguous_finger(self):
                self.adduser('admintwo', 'admintwo')
                t = self.connect_as_admin()

                t.write('finger ad\r\n')
                self.expect('Finger of admin(*):', t, "finger with prefix ignores offline user")
                t2 = self.connect_as_user('admintwo', 'admintwo')
                # ambiguous, both users online 
                t2.write('finger ad\r\n')
                self.expect('Matches: admin admintwo', t2)
                self.close(t2)
                self.close(t)
               
                # ambiguous, both users offline 
                t = self.connect_as_guest()
                t.write('finger ad\r\n')
                self.expect('Matches: admin admintwo', t)
                self.close(t)

                self.deluser('admintwo')
        
        def test_finger_guest(self):      
                t = self.connect_as_guest()

                # finger guest
                t.write('finger\r\n')
                self.expect('Finger of Guest', t)

                # finger offline user
                t.write('finger admin\r\n')
                self.expect('Last disconnected:', t)
               
                # finger offline user prefix
                t.write('finger ad\r\n')
                self.expect('Last disconnected:', t)
                
                t.write('finger admi\r\n')
                self.expect('Last disconnected:', t)

                t.close()


# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent ft=python
