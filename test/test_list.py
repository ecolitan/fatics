from test import *

class TestList(Test):
    def test_list_error(self):
        t = self.connect_as_guest()

        t.write('addlist foo bar\n')
        self.expect("does not match any list", t)

        t.write('sublist foo bar\n')
        self.expect("does not match any list", t)

        t.write('+g admin\n')
        self.expect("You don't have permission", t)

        self.close(t)
    
    def test_list_add_sub(self):
        # see also test_title; this tests persistence
        t = self.connect_as_admin()

        t.write('+gm admin\n')
        self.expect("admin added to the GM list.", t)

        t.write('t admin foo bar\n')
        self.expect('admin(GM)(*) tells you: foo bar', t)
        self.close(t)

        t = self.connect_as_admin()
        t.write('t admin foo bar\n')
        self.expect('admin(GM)(*) tells you: foo bar', t)

        t.write('-gm admin\n')
        self.expect("admin removed from the GM list.", t)
        self.close(t)

        
        t = self.connect_as_admin()
        t.write('t admin foo bar\n')
        self.expect('admin(*) tells you: foo bar', t)
        self.close(t)

'''
class TestCensor(Test):
    def test_censor_guest(self):
        t = self.connect_as_user('GuestABCD', '')
        t2 = self.connect_as_user('GuestDEFG', '')

        t.write('+cen guestdefg\n')
        self.expect('GuestDEFG added to your censor list.', t)

        self.close(t)
        self.close(t2)'''

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
