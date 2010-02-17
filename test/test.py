#!/usr/bin/env python
import sys
import telnetlib
import socket
import unittest
import os

if True:
	host = 'localhost'
	port = '5000'
else:
	host = 'sheila'
	port = '5000'
admin_passwd = 'admin'

tests = []
class Test(object):
	def __init__(self):
		tests.append(self)
		self.passed = 0
		self.total = 0

	def run(self):
		"""This method should call yes() and no() as many times as
		desired to indicate whether tests succeed."""
		pass

	def yes(self, msg):
		self.passed = self.passed + 1
		self.total = self.total + 1
		print 'PASS: %s: %s' % (self.__class__.__name__, msg)

	def no(self, msg):
		self.total = self.total + 1
		print 'FAIL: %s: %s' % (self.__class__.__name__, msg)

	def test(self, test, msg):
		if test:
			self.yes(msg)
		else:
			self.no(msg)

	def expect_exact(self, str, t, msg, timeout=2):
		ret = t.read_until(str, timeout)
		if str in ret:
			self.yes(msg)
		else:
			self.no(msg)
	
	def expect_EOF(self, t, msg):
		try:
			ret = t.read_very_eager()
			ret = t.read_until('not-seen', 2)
		except EOFError:
			self.yes(msg)
		else:
			self.no(msg)

	def connect(self, login='admin\r\n%s\r\n' % admin_passwd):
		t = connect()
		if login:
			t.write(login)
			t.read_until('fics%')
		return t
	
	
def connect():
	try:
		t = telnetlib.Telnet(host, port, 120)
	except socket.gaierror:
		t = None
	except socket.error:
		t = None
	return t

class ConnectTest(Test):
	def run(self):
		t = self.connect(None)

		# welcome message
		self.expect_exact('Welcome', t, "welcome message")

		self.expect_exact('login:', t, "login prompt")

		t.close()
ConnectTest()

class LoginTest(Test):
	def run(self):
		# anonymous guest
		t = self.connect(None)

		t.read_until('login:', 2)
		t.write('\r\n')
		self.expect_exact('login:', t, "blank line at login prompt")

		t.write('ad\r\n')
		self.expect_exact('name should be at least', t, "login username too short")
		
		t.write('adminabcdefghijklmno\r\n')
		self.expect_exact('names may be at most', t, "login username too long")
		
		t.write('admin1\r\n')
		self.expect_exact('names can only consist', t, "login username contains numbers")

		t.write('guest\r\n')
		self.expect_exact('Press return to enter', t, "anonymous guest login start")
		
		t.write('\r\n')
		self.expect_exact(' Starting', t, "anonymous guest login complete")
		t.close()

		# registered user
		t = self.connect(None)
		t.write('admin\r\n')
		self.expect_exact('is a registered', t, "registered user login start")

		t.write(admin_passwd + '\r\n')
		self.expect_exact(' Starting', t, "registered user login complete")
		t.close()
LoginTest()

class PromptTest(Test):
	def run(self):
		t = self.connect(None)
		t.write('guest\r\n\r\n')
		self.expect_exact('fics%', t, "fics% prompt")
		t.close()
PromptTest()

class FingerTest(Test):
	def run(self):
		t = connect()
		t.write('admin\r\n%s\r\n' % admin_passwd)
		[i, m, text] = t.expect(['fics%'], 2)
		t.write('finger\r\n')
		[i, m, text] = t.expect(['Finger of admin:'], 2)
		self.test(i == 0, "finger")
		[i, m, text] = t.expect(['On for:'], 2)
		self.test(i == 0, "finger of online user")
		
		t.write('finger \r\n')
		[i, m, text] = t.expect(['Finger of admin:'], 2)
		self.test(i == 0, "finger with trailing space")

		t.write('finger admin\r\n')
		[i, m, text] = t.expect(['Finger of admin:'], 2)
		self.test(i == 0, "finger with parameter")
		
		t.write('finger ad\r\n')
		[i, m, text] = t.expect(['Finger of admin:'], 2)
		self.test(i == 0, "finger with prefix")

		t.write('addplayer admintwo nobody@example.com Admin Two\r\n')
		t.write('asetpass admintwo admintwo\r\n')
		t.write('finger ad\r\n')
		[i, m, text] = t.expect(['Finger of admin:'], 2)
		self.test(i == 0, "finger with prefix ignores offline user")
		t2 = connect()
		t2.write('admintwo\r\nadmintwo\r\n')
		[i, m, text] = t2.expect(['fics%'], 2)
		t2.write('finger ad\r\n')
		[i, m, text] = t2.expect(['Matches: admin admintwo'], 2)
                self.test(i == 0, "finger ambiguous online users")
		t2.close()
		t.write('remplayer admintwo\r\n')
		[i, m, text] = t.expect(['removed'], 2)
		
		t.write('finger notarealuser\r\n')
		[i, m, text] = t.expect(['no player matching'], 2)
		self.test(i == 0, "nonexistent user")
		
		t.write('finger admin1\r\n')
		[i, m, text] = t.expect(['not a valid handle'], 2)
		self.test(i == 0, "invalid name")

		t.close()
		
		t = self.connect('guest\r\n\r\n')
		t.read_until('fics%', 2)
		t.write('finger admin\r\n')
		self.expect_exact('Last disconnected:', t, "finger offline user")
		
		t.write('finger admi\r\n')
		self.expect_exact('Last disconnected:', t, "finger offline user prefix")
		t.close()
FingerTest()


class AddplayerTest(Test):
	def run(self):
		t = self.connect()
		t.write('addplayer testplayer nobody@example.com Foo Bar\r\n')
		self.expect_exact('Added:', t, 'addplayer')
		t.write('addplayer testplayer nobody@example.com Foo Bar\r\n')
		self.expect_exact('already registered', t, 'addplayer duplicate player')
		t.write('remplayer testplayer\r\n')
		t.close()
AddplayerTest()

class TelnetTest(Test):
	def run(self):
		t = self.connect()
		t.read_until('fics%', 2)
		os.write(t.fileno(), chr(255) + chr(244))
		self.expect_EOF(t, "interrupt connection")
		t.close()
TelnetTest()

class TimeoutTest(Test):
	def run(self):
		t = self.connect(None)
		self.expect_exact('TIMEOUT', t, "login timeout", timeout=65)
		t.close()
		
		t = self.connect(None)
		t.write("guest\r\n")
		self.expect_exact('TIMEOUT', t, "login timeout at password prompt", timeout=65)
		t.close()
		
		t = self.connect(None)
		t.write("guest\r\n")
		self.expect_exact('TIMEOUT', t, "login timeout guest", timeout=65)
		t.close()
TimeoutTest()

class AreloadTest(Test):
	def run(self):
		t = self.connect()
		t.write('areload\r\n')
		self.expect_exact('reloaded online', t, "server reload")
		t.close()
AreloadTest()

def main():
	t = connect()
	if not t:
		print 'ERROR: Unable to connect.  A running server is required to do the tests.\r\n'
		sys.exit(1)
	t.close()

	total = 0
	passed = 0	
	for test in tests:
		test.run()
		total = total + test.total
		passed = passed + test.passed
	print "Passed %d/%d tests." % (passed, total)

if __name__ == "__main__":
	main()
