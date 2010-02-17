#!/usr/bin/env python
import sys
import telnetlib
import socket
import os
from twisted.trial import unittest
#import unittest

if True:
	host = 'localhost'
	port = '5000'
else:
	host = 'sheila'
	port = '5000'
admin_passwd = 'admin'

def connect():
	try:
		t = telnetlib.Telnet(host, port, 120)
	except socket.gaierror:
		t = None
	except socket.error:
		t = None
	return t

class Test(unittest.TestCase):
	def expect(self, str, t, msg, timeout=2):
		ret = t.read_until(str, timeout)
		self.assert_(str in ret)
	
	def expect_EOF(self, t, msg):
		def read_some(unused):
			t.read_very_eager()
			t.read_until('not-seen', 2)
		self.assertRaises(EOFError, read_some, msg)

	def connect(self):
		return connect()
	
	def connect_as_guest(self):
		t = connect()
		t.write("guest\r\n\r\n")
		t.read_until('fics%', 2)
		return t
	
	def connect_as_admin(self):
		t = connect()
		t.write("admin\r\n%s\r\n" % admin_passwd)
		t.read_until('fics%', 2)
		return t

class OneConnectionTest(Test):
	def setUp(self):
		self.t = self.connect()

	def tearDown(self):
		self.t.close()

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
		t.close()

	def testRegisteredUserLogin(self):
		# registered user
		t = self.connect()
		t.write('admin\r\n')
		self.expect('is a registered', t, "registered user login start")

		t.write(admin_passwd + '\r\n')
		self.expect(' Starting', t, "registered user login complete")
		t.close()

class PromptTest(Test):
	def testPrompt(self):
		t = self.connect()
		t.write('guest\r\n\r\n')
		self.expect('fics%', t, "fics% prompt")
		t.close()

class FingerTest(Test):
	def testFinger(self):
		t = self.connect_as_admin()
		t.write('finger\r\n')
		self.expect('Finger of admin:', t, "finger")
		self.expect('On for:', t, "finger of online user")
		
		t.write('finger \r\n')
		self.expect('Finger of admin:', t, "finger with trailing space")

		t.write('finger admin\r\n')
		self.expect('Finger of admin:', t, "finger with parameter")
		
		t.write('finger ad\r\n')
		self.expect('Finger of admin:', t, "finger with prefix")

		t.write('addplayer admintwo nobody@example.com Admin Two\r\n')
		t.write('asetpass admintwo admintwo\r\n')
		t.write('finger ad\r\n')
		self.expect('Finger of admin:', t, "finger with prefix ignores offline user")
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


class AddplayerTest(Test):
	def testAddplayer(self):
		t = self.connect_as_admin()
		t.write('addplayer testplayer nobody@example.com Foo Bar\r\n')
		self.expect('Added:', t, 'addplayer')
		t.write('addplayer testplayer nobody@example.com Foo Bar\r\n')
		self.expect('already registered', t, 'addplayer duplicate player')
		t.write('remplayer testplayer\r\n')
		t.close()

class TelnetTest(Test):
	def testTelnet(self):
		t = self.connect()
		t.read_until('fics%', 2)
		os.write(t.fileno(), chr(255) + chr(244))
		self.expect_EOF(t, "interrupt connection")
		t.close()

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
		
	def testGuestTimeout(self):	
		t = self.connect()
		t.write("guest\r\n")
		self.expect('TIMEOUT', t, "login timeout guest", timeout=65)
		t.close()

"""not stable
class AreloadTest(Test):
	def runTest(self):
		self.skip()
		t = self.connect()
		t.write('areload\r\n')
		self.expect('reloaded online', t, "server reload")
		t.close()
"""

def check_server():
	t = connect()
	if not t:
		print 'ERROR: Unable to connect.  A running server is required to do the tests.\r\n'
		sys.exit(1)
	t.close()
	
check_server()

if __name__ == '__main__':
	exit('this should be run using trial')


