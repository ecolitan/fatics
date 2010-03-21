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
    
    def test_list_persistence(self):
        # see also test_title; this tests persistence
        t = self.connect_as_admin()

        t.write('+sr admin\n')
        self.expect("admin added to the SR list.", t)

        t.write('t admin foo bar\n')
        self.expect('admin(SR)(*) tells you: foo bar', t)
        self.close(t)

        t = self.connect_as_admin()
        t.write('t admin foo bar\n')
        self.expect('admin(SR)(*) tells you: foo bar', t)

        t.write('-sr admin\n')
        self.expect("admin removed from the SR list.", t)
        self.close(t)

        t = self.connect_as_admin()
        t.write('t admin foo bar\n')
        self.expect('admin(*) tells you: foo bar', t)
        self.close(t)

class TestTitle(Test):
    def test_bad_name(self):
        t = self.connect_as_admin()
        t.write('+gm nonexistentname\n')
        self.expect("no player matching", t)
        self.close(t)

    def test_title(self):
        t2 = self.connect_as_guest()
        t2.write('+gm admin\n')
        self.expect("You don't have permission", t2)

        t = self.connect_as_admin()
        t.write('+gm guest\n')
        self.expect('nly registered users may', t)
        self.close(t2)

        t.write('+gm admin\n')
        self.expect("admin added to the GM list", t)

        t.write('t admin a b c\n')
        self.expect("admin(GM)(*) tells you: a b c", t)

        t.write('+gm admin\n')
        self.expect("admin is already on the GM list", t)

        t.write('-gm admin\n')
        self.expect("admin removed from the GM list", t)

        t.write('-gm admin\n')
        self.expect("admin is not on the GM list", t)

        t.write('t admin d e f\n')
        self.expect("admin(*) tells you: d e f", t)

        self.close(t)

class TestCensor(Test):
    def test_censor_guest(self):
        t = self.connect_as_user('GuestABCD', '')
        t2 = self.connect_as_user('GuestDEFG', '')
        
        t.write('+cen Nosuchplayer\n')
        self.expect('There is no player matching the name "nosuchplayer".', t)

        t.write('-cen admin\n')
        self.expect('admin is not on your censor list.', t)

        t.write('+cen guestdefg\n')
        self.expect('GuestDEFG added to your censor list.', t)

        t2.write('t guestABCD hi\n')
        self.expect('GuestABCD is censoring you.', t2)
        
        t2.write('m guestabcd\n')
        self.expect('GuestABCD is censoring you.', t2)
        
        t.write('-cen guestdefg\n')
        self.expect('GuestDEFG removed from your censor list.', t)
        
        t2.write('t guestabcd hi again\n')
        self.expect('(told GuestABCD)', t2)
        self.expect('GuestDEFG(U) tells you: hi again', t)
        self.close(t2)

        t2 = self.connect_as_admin()
        t.write('+cen admin\n')
        self.expect('admin added to your censor list', t)

        t2.write("t guestabcd You can't censor me\n")
        self.expect("You can't censor me", t)

        self.close(t2)
        self.close(t)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
