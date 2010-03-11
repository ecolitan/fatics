from test import *

class TestMatch(Test):
    def test_match(self):
        t = self.connect_as_guest()
        t2 = self.connect_as_admin()

        t.write('match guest\n')
        self.expect("can't match yourself", t)

        t.write('match nonexistentname\n')
        self.expect('No user named "nonexistentname"', t)

        t.write('set open 0\n')
        t2.write('set open 0\n')
        t.write('match admin\n')
        self.expect('admin is not open to match requests', t)

        t2.write('set open 1\n')
        self.expect('now open', t2)
        t.write('match admin\n')
        self.expect('now open to receive match requests', t)
        self.expect('Issuing: ', t)
        self.expect('Challenge: ', t2)

        self.close(t)
        self.close(t2)
    
    def test_withdraw_logout(self):
        t = self.connect_as_guest()
        t2 = self.connect_as_admin()
        t2.write('match guest\n')
        t2.write('quit\n')
        self.expect('Withdrawing your offer to Guest', t2)
        self.expect('Thank you for using', t2)
        t2.close()

        self.expect('admin, who was challenging you, has departed', t)
        self.close(t)
    
    def test_decline_logout(self):
        t = self.connect_as_user('GuestABCD', '')
        t2 = self.connect_as_admin()

        t.write('match admin\n')
        self.expect('Challenge:', t2)
        t2.write('quit\n')
        self.expect('Declining the offer from Guest', t2)
        t2.close()

        self.expect('admin, whom you were challenging, has departed', t)
        self.close(t)

    def test_accept(self):
        t = self.connect_as_guest()
        t2 = self.connect_as_admin()
        
        t.write('match admin\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('Accepting the offer', t2)
        self.expect('accepts your offer', t)
        
        self.expect('Creating: ', t)
        self.expect('Creating: ', t2)

        self.close(t)
        self.close(t2)

    def test_withdraw(self):
        t = self.connect_as_guest()
        t2 = self.connect_as_admin()
        
        t.write('match admin\n')
        self.expect('Challenge:', t2)
        t.write('withdraw\n')
        self.expect('Withdrawing your offer', t)
        self.expect('withdraws the offer', t2)

        self.close(t)
        self.close(t2)
    
    def test_decline(self):
        t = self.connect_as_guest()
        t2 = self.connect_as_admin()
        
        t.write('match admin\n')
        self.expect('Challenge:', t2)
        t2.write('decline\n')
        self.expect('Declining the offer', t2)
        self.expect('declines the offer', t)

        self.close(t)
        self.close(t2)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
