import re
import admin

class Command:
	def __init__(self, name, run, adminlevel):
		self.name = name
		self.run = run
		self.adminlevel = adminlevel

class QuitException(Exception):
	pass

class CommandList():
	def __init__(self):
		self.cmds = {}
		self.add_command(Command('finger', self.finger, admin.Level.user))
		self.add_command(Command('quit', self.quit, admin.Level.user))

	def add_command(self, cmd):
		self.cmds[cmd.name] = cmd

	def finger(self, args, conn):
		conn.write('finger of %s\n' % conn.user.name)
	
	def quit(self, args, conn):
		raise QuitException()
		

command_list = CommandList()

def handle_command(s, conn):
	m = re.match('^(\S+)(?: (.*))?$', s)
	if m:
		cmd = m.group(1)
		if cmd in command_list.cmds:
			command_list.cmds[cmd].run(m.group(2), conn)
		else:
                	conn.write("%s: Command not found.\n" % cmd)
	else:
                conn.write("Command not found.\n")


