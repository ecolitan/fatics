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


# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
