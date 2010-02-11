import re
import trie
import admin

class Command:
	def __init__(self, name, aliases, run, adminlevel):
		self.name = name
		self.aliases = aliases
		self.run = run
		self.adminlevel = adminlevel

class QuitException(Exception):
	pass

class CommandList():
	def __init__(self):
		# the trie data structure allows for efficiently finding
		# a command given a substring
		self.cmds = trie.Trie()
		self.add_command(Command('finger', ['f'], self.finger, admin.Level.user))
		self.add_command(Command('follow', [], self.follow, admin.Level.user))
		self.add_command(Command('quit', [], self.quit, admin.Level.user))

	def add_command(self, cmd):
		self.cmds[cmd.name] = cmd
		for a in cmd.aliases:
			self.cmds[a] = cmd

	def finger(self, args, conn):
		conn.write('finger of %s\n' % conn.user.name)
	
	def follow(self, args, conn):
		conn.write('FOLLOW')
	
	def quit(self, args, conn):
		raise QuitException()
		

command_list = CommandList()

def handle_command(s, conn):
	m = re.match('^(\S+)(?: (.*))?$', s)
	cmd = None
	if m:
		word = m.group(1)
		try:
			cmd = command_list.cmds[word]
		except KeyError:
                	conn.write("%s: Command not found.\n" % cmd)
		except trie.NeedMore:
                	matches = command_list.cmds.all_children(word)
			assert(len(matches) > 0)
			if len(matches) == 1:
				cmd = matches.pop()
			else:
                		conn.write("""Ambiguous command "%s". Matches: %s\n""" % (word, ' '.join([c.name for c in matches])))
		if cmd:
			cmd.run(m.group(2), conn)
	else:
                conn.write("Command not found.\n")


