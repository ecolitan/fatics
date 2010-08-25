from test import *

class TestVarsCommand(Test):
    def test_self_vars(self):
        t = self.connect_as_admin()
        t.write('vars\n')
        self.expect('Variable settings of admin:', t)
        self.expect('shout=1', t)
        self.close(t)

    def test_self_vars_guest(self):
        t = self.connect_as_guest()
        t.write('vars\n')
        self.expect('Variable settings of Guest', t)
        self.expect('shout=1', t)
        self.close(t)

    def test_other_vars(self):
        t = self.connect_as_guest()
        t.write('vars admin\n')
        self.expect('Variable settings of admin:', t)
        self.expect('shout=1', t)
        self.close(t)
    
    def test_self_ivars(self):
        t = self.connect_as_admin()
        t.write('ivars\n')
        self.expect('Interface variable settings of admin:', t)
        self.expect('smartmove=0', t)
        self.close(t)

    def test_other_ivars(self):
        t = self.connect_as_guest()
        t2 = self.connect_as_admin()
        t.write('ivars admin\n')
        self.expect('Interface variable settings of admin:', t)
        self.expect('smartmove=0', t)
        self.close(t)
        self.close(t2)
    
    def test_ivars_offline(self):
        t = self.connect_as_guest()
        t.write('ivars admin\n')
        self.expect('No user named "admin" is logged in', t)
        self.close(t)

class TestVars(Test):
    def test_vars(self):
        t = self.connect_as_guest()

        t.write("set tell 0\n")
        self.expect("You will not hear direct tells from unregistered", t)
        t.write("set tell 1\n")
        self.expect("You will now hear direct tells from unregistered", t)
        t.write("set shout 0\n")
        self.expect("You will not hear shouts", t)
        t.write("set shout 1\n")
        self.expect("You will now hear shouts", t)

        t.write("set open 0\n")
        self.expect("no longer open to receive match requests", t)
        t.write("set open 1\n")
        self.expect("are now open to receive match requests", t)
        t.write("set open 2\n")
        self.expect('Bad value given for variable "open"', t)

        t.write("set style -1\n")
        self.expect('Bad value given for variable "style"', t)
        
        t.write("set lang Klingon\n")
        self.expect('Bad value given for variable "lang"', t)
        
        t.write("set style 100\n")
        self.expect('Bad value given for variable "style"', t)

        self.close(t)
    
    def test_prompt(self):
        t = self.connect_as_guest()
        t.write('set prompt foobar%\n')
        self.expect('prompt set to "foobar% ".', t)
        
        t.write('fi\n')
        self.expect('Finger of Guest', t)
        self.expect('foobar% ', t)
        self.close(t)
    
    def test_transient_var_user(self):
        t = self.connect_as_admin()
        t.write('set interface Thief 1.23 Midget edition\n')
        self.expect('interface set to "Thief 1.23 Midget edition"', t)
        self.close(t)

class TestIvars(Test):
    def test_ivars(self):
        t = self.connect_as_guest()

        t.write("iset smartmove 1\n")
        self.expect("smartmove set", t)

        t.write("iset smartmove 0\n")
        self.expect("smartmove unset", t)

        self.close(t)

    def test_login_ivars(self):
        t = self.connect()
        t.write('%b000000000000000000000000000000000\n')
        self.expect("Ivars set.", t)
        t.close()


class TestGameinfo(Test):
    def test_gameinfo(self):
        t = self.connect_as_guest()
        t2 = self.connect_as_admin()
        t.write("match admin 2 12 u white\n")
        t.write('iset gamei 1\n')
        self.expect('gameinfo set.', t)
        self.expect("Challenge:", t2)
        t2.write('a\n')

        self.expect('<g1> 1 p=0 t=chess r=0 u=1,0 it=120,12 i=120,12 pt=0 rt=0,0 ts=0,0 m=2 n=0', t)
        t.write('abort\n')

        self.close(t)
        self.close(t2)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
