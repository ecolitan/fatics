from test import *

class TestAlias(Test):
    def test_alias(self):
        t = self.connect_as_admin()
        t.write('t admin test 1\n')
        self.expect('admin(*) tells you: test 1', t)

        t.write('.test 2\n')
        self.expect('admin(*) tells you: test 2', t)

        self.close(t)

class TestSystemAlias(Test):
    def test_system(self):
        t = self.connect_as_admin()

        t.write('+ch 1\n')
        t.write('answer handle foo bar baz\n')
        self.expect('(1): (answering handle): foo bar baz', t)

        t.write('answer\n')
        self.expect('(1): (answering ): ', t)

        t.write('! blah blah\n')
        self.expect('shouts: blah blah', t)
        t.write('-ch 1\n')

        self.close(t)

class TestUserAlias(Test):
    def test_guest_alias(self):
        t = self.connect_as_guest()

        t.write('alias\n')
        self.expect('You have no aliases', t)

        t.write('alias foo\n')
        self.expect('You have no alias named "foo"', t)
        
        t.write('alias foo finger\n')
        self.expect('Alias "foo" set.', t)
        
        t.write('foo\n')
        self.expect('Finger of Guest', t)

        t.write('alias foo\n')
        self.expect('foo -> finger', t)

        t.write('alias foo finger $@\n')
        self.expect('Alias "foo" changed.', t)

        t.write('foo admin\n')
        self.expect('Finger of admin', t)

        t.write('unalias foo\n')
        self.expect('Alias "foo" unset.', t)
        
        t.write('unalias nosuchvar\n')
        self.expect('You have no alias "nosuchvar".', t)

        self.close(t)
    
    def test_user_alias(self):
        t = self.connect_as_admin()

        t.write('alias bar\n')
        self.expect('You have no alias named "bar"', t)
        
        t.write('alias bar shout my name is $m\n')
        self.expect('Alias "bar" set.', t)

        self.close(t)
        
        t = self.connect_as_admin()
        t.write('alias bar\n')
        self.expect('bar -> shout my name is $m', t)

        t.write('bar\n')
        self.expect('shouts: my name is admin', t)

        t.write('alias bar tell admin hi there\n')
        self.expect('Alias "bar" changed.', t)

        t.write('bar ignored\n')
        self.expect('tells you: hi there', t)

        t.write('unalias bar\n')
        self.expect('Alias "bar" unset.', t)
        
        t.write('unalias nosuchvar\n')
        self.expect('You have no alias "nosuchvar".', t)

        self.close(t)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

