import re
import time

import user
import trie
import admin

class InternalException(Exception):
	pass
class QuitException(Exception):
	pass
class BadCommandException(Exception):
	pass

class Command:
	def __init__(self, name, aliases, param_str, run, adminlevel):
		self.name = name
		self.aliases = aliases
		self.param_str = param_str
		self.run = run
		self.adminlevel = adminlevel

	def parse_params(self, s):
		params = []
		for c in self.param_str:
			if c in ['i', 'w']:
				# required argument
				if s == None:
					raise BadCommandException()
				else:
					m = re.split(r'\s+', s, 1)
					assert(len(m) > 0)
					param = m[0].lower()
					assert(len(param) > 0)
					if len(param) == 0:
						raise BadCommandException()
					s = m[1] if len(m) > 1 else None
			elif c in ['o', 'n']:
				# optional argument
				if s == None:
					param = None
				else:
					m = re.split(r'\s+', s, 1)
					assert(len(m) > 0)
					param = m[0].lower()
					assert(len(param) > 0)
					if len(param) == 0:
						param = None
						assert(len(m) == 1)
					s = m[1] if len(m) > 1 else None
			elif c == 'S':
				# string to end
				if s == None or len(s) == 0:
					raise BadCommandException()
				param = s
				s = None
			else:
				raise InternalException()
			params.append(param)

		if not (s == None or re.match(r'\s*', s)):
			# extraneous data at the end
			raise BadCommandException()
				
		return params

	def help(self, conn):
		conn.write("help for %s\n" % self.name)

class CommandList():
	def __init__(self):
		# the trie data structure allows for efficiently finding
		# a command given a substring
		self.cmds = trie.Trie()
		self.add_command(Command('finger', ['f'], 'ooo', self.finger, admin.Level.user))
		self.add_command(Command('follow', [], 'w', self.follow, admin.Level.user))
		self.add_command(Command('quit', [], '', self.quit, admin.Level.user))
		self.add_command(Command('tell', ['t'], 'nS', self.tell, admin.Level.user))

	def add_command(self, cmd):
		self.cmds[cmd.name] = cmd
		for a in cmd.aliases:
			self.cmds[a] = cmd

	def finger(self, args, conn):
		try:
			if args[0] != None:
				u = user.find.by_name(args[0])
			else:
				u = conn.user
		except user.UsernameException:
			conn.write('"%s" is not a valid handle\n.' % args[0])
		else:
			if not u:
				# XXX substring matches
				conn.write('There is no player matching the name "%s".\n' % args[0])
			else:
				conn.write('Finger of %s:\n\n' % u.get_display_name())
				if u.is_online:
					conn.write('On for: %s   Idle: %s\n\n' % (u.session.get_online_time(), u.session.get_idle_time()))
					
				else:
					if u.last_logout == None:
						conn.write('%s has never connected.\n\n' % u.name)
					else:
						conn.write('Last disconnected: %s\n\n' % u.last_logout)

	
	def follow(self, args, conn):
		conn.write('FOLLOW')
	
	def tell(self, args, conn):
		try:
			u = user.find.by_name(args[0])
		except user.UsernameException:
			conn.write('"%s" is not a valid handle.\n' % args[0])
		else:
			if not u:
				conn.write('There is no player matching the name "%s".\n' % args[0])
			elif not u.is_online:
				conn.write('%s is not logged in.' % args[0])
			else:
				u.write('\n' + conn.user.get_display_name() + " tells you: " + args[1] + '\n')
				
	
	def quit(self, args, conn):
		raise QuitException()
		

command_list = CommandList()

def handle_command(s, conn):
	conn.user.session.last_command_time = time.time()
	m = re.match(r'^(\S+)(?:\s+(.*))?$', s)
	cmd = None
	if m:
		word = m.group(1)
		try:
			cmd = command_list.cmds[word]
		except KeyError:
                	conn.write("%s: Command not found.\n" % word)
		except trie.NeedMore:
                	matches = command_list.cmds.all_children(word)
			assert(len(matches) > 0)
			if len(matches) == 1:
				cmd = matches.pop()
			else:
                		conn.write("""Ambiguous command "%s". Matches: %s\n""" % (word, ' '.join([c.name for c in matches])))
		if cmd:
			try:
				cmd.run(cmd.parse_params(m.group(2)), conn)
			except BadCommandException:
				cmd.help(conn)
	else:
                conn.write("Command not found.\n")


