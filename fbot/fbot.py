#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2010  Wil Mahan <wmahan+fatics@gmail.com>
#
# This file is part of FatICS.
#
# FatICS is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# FatICS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with FatICS.  If not, see <http://www.gnu.org/licenses/>.
#

import time
import string
import re
import bcrypt
import random
import MySQLdb

import icsbot

username = 'fbot'
password = ''
host = 'localhost'
#host = 'freechess.org'
port = 5000
db_host = 'localhost'
db_db = 'chess'

pass_min = 4
pass_max = 6

server_address = 'fatics.dyndns.org port 5000'

notes = [
    "This bot helps you try FatICS, an experimental chess server.",
    '\"tell %s register\" will generate a password for you.' % username,
    'Then log in with your FICS name at %s.' % server_address,
    'You can also connect to the above address as a guest, without registering.',
    "At the moment I'm an unregistered bot, so \"set tell 1\" first.",
    'Thanks for testing!',
    '--',
    "This bot was written by wmahan using seberg's bot framework (finger seberg for details).  Source code: http://bitbucket.org/wmahan/fatics",
    'Contact: wmahan',
]

known_titles = [
    '*', 'CM', 'FM', 'IM', 'GM', 'WCM', 'WFM', 'WIM', 'WGM',
    'B', 'C', 'CA', 'TM', 'TD', 'SR', 'U'
]

""" transient or obsolete vars """
ignored_vars = [
    'rated', 'availinfo', 'availmin', 'availmax',
    'pgn', 'tourney', 'tolerance', 'kiblevel', 'flip'
]

# convert the languages FICS knows about into ISO 639-1 codes
# for FatICS
language_codes = {
    'Danish': 'da',
    'English': 'en',
    'French': 'fr',
    'German': 'de',
    'Italian': 'it',
    'Russian': 'ru',
    'Spanish': 'es',
    'Turkish': 'tr',
}

good_interface_re = re.compile('(?:XBoard).*')
bad_interface_re = re.compile('(?:Thief|Jin).*')

bot_admins = ['wmahan']

example_vars = """
Variable settings of GuestPQJM:

time=2       private=0     shout=0         pin=0           style=12 
inc=12       jprivate=0    cshout=0        notifiedby=0    flip=0
rated=0                    kibitz=1        availinfo=0     highlight=0
open=1       automail=0    kiblevel=0      availmin=0      bell=0
             pgn=0         tell=1          availmax=0      width=80 
bugopen=0                  ctell=1         gin=0           height=24 
             mailmess=0                    seek=0          ptime=0
tourney=0    messreply=0   chanoff=1       showownseek=0   tzone=SERVER
provshow=0                 silence=0                       Lang=English
autoflag=1   unobserve=1   echo=1          examine=0
minmovetime=1              tolerance=1     noescape=0      notakeback=0

Interface: "BabasChess 4.0 Build 12274"
"""

"""
Variable settings of blik:

time=5       private=0     shout=1         pin=0           style=12 
inc=0        jprivate=0    cshout=0        notifiedby=1    flip=0
rated=1                    kibitz=1        availinfo=0     highlight=0
open=1       automail=0    kiblevel=0      availmin=0      bell=0
             pgn=1         tell=1          availmax=0      width=240
bugopen=0                  ctell=1         gin=0           height=24 
             mailmess=0                    seek=0          ptime=0
tourney=0    messreply=0   chanoff=0       showownseek=0   tzone=???
provshow=0                 silence=0                       Lang=English
autoflag=1   unobserve=1   echo=1          examine=0
minmovetime=0              tolerance=1     noescape=1      notakeback=0

Prompt: aics% 
Interface: "RookICS marcelk-20061212 + ./rookie"

 f1: 2<=time                      # Don't play Space Invaders on the board
 f2: inc<=10 & time<=10           # And don't spend hours on a move
 f3: rated & 1<=assesswin         # No chicken please
 f4: blitz | lightning            # Chess is chess is chess...
 f5: !abuser & !private & nocolor # It's a noble game
 f6: 
 f7: # Please ask marcelk whenever you'ld like to play with other settings!

Formula: f1 & f2 & f3 & f4 & f5 & (rating>0) & !computer
"""

class DB(object):
    def __init__(self):
        self.db = MySQLdb.connect(host=db_host, db=db_db,
            read_default_file="~/.my.cnf")

    def user_add(self, user_name, user_email, user_passwd, user_real_name,
            user_fics_name, user_admin_level):
        cursor = self.db.cursor()
        try:
            cursor.execute("""INSERT INTO user SET user_name=%s,user_email=%s,user_passwd=%s,user_real_name=%s,user_fics_name=%s,user_admin_level=%s""", (user_name,user_email,user_passwd,user_real_name,user_fics_name,user_admin_level))
        except:
            cursor.close()
            raise
        ret = cursor.lastrowid
        cursor.close()
        return ret

    def user_set_vars(self, user_id, vars):
        cursor = self.db.cursor()
        vars_str = ','.join([k + '=%(' + k + ')s' for (k,v) in vars.iteritems()])
        query = ("UPDATE user SET %s WHERE user_id=" % vars_str) + '%(user_id)s'
        vars['user_id'] = user_id
        cursor.execute(query, vars)
        cursor.close()

    def user_set_formula(self, user_id, formula):
        cursor = self.db.cursor()
        for (k, v) in formula.iteritems():
            cursor.execute('INSERT INTO formula SET user_id=%s,num=%s,f=%s',
                (user_id, k, v))
        cursor.close()

    def set_note(self, user_id, num, txt):
        cursor = self.db.cursor()
        cursor.execute('INSERT INTO note SET user_id=%s,num=%s,txt=%s',
            (user_id, num, txt))
        cursor.close()

    def grant_title(self, user_id, title_flag):
        cursor = self.db.cursor()
        cursor.execute('''INSERT INTO user_title
            SET user_id=%s,title_id=(SELECT title_id FROM TITLE
                WHERE title_flag=%s)''' %
            (user_id, title_flag))
        cursor.close()

class FBot(icsbot.IcsBot):
    def __init__(self, qtell_dummy=True, unmatched_log=None, tell_logger=None):
        super(FBot, self).__init__(qtell_dummy=True, unmatched_log=None, tell_logger=tell_logger)


        self.reg_tell('register', self.register)
        self.reg_tell('help', self.help)
        self.db = DB()

        # wrapping long lines would interfere with parsing finger notes
        self.send('iset nowrap 1')

        # try to limit unnecessary messages from the server
        self.send('set open 0')
        self.send('set seek 0')
        self.send('set shout 0')
        self.send('set cshout 0')
        self.send('set highlight 0')
        self.send('set chanoff 1')
        assert(len(notes) <= 10)
        for (i, note) in enumerate(notes):
            self.send('set %d %s' % (i + 1, note))

    def _make_passwd(self):
        chars = string.letters + string.digits
        passlen = random.choice(range(pass_min, pass_max))
        ret = []
        for i in range(passlen):
            ret.append(random.choice(chars))
        return ''.join(ret)

    crlf = re.compile('(?:\n\r|\r\n|\n)')
    formula_re = re.compile('(?:Formula| f([1-9])): (.*)')
    interface_re = re.compile('Interface: "(.*)"')
    prompt_re = re.compile('Prompt: (.*)')
    var_re = re.compile('([A-Za-z]+)=(\w+)')
    def copy_vars(self, *args, **kwargs):
        (data, usr, tags, passwd, user_id) = args
        #data = example_vars
        print "copy_vars: %r" % data
        vars = {}
        formula = {}
        interface = None
        lines = re.split(self.crlf, data)
        for line in lines:
            if line.startswith('Variable settings of'):
                continue
            if line.strip() == '':
                continue
            m = self.formula_re.match(line)
            if m:
                if not m.group(1):
                    # main formula var
                    formula[0] = m.group(2)
                else:
                    formula[int(m.group(1))] = m.group(2)
                continue
            m = self.prompt_re.match(line)
            if m:
                continue
            m = self.interface_re.match(line)
            if m:
                # don't store these values, but we can check
                # the user's interface for compatibility.
                interface = m.group(1)
                continue

            # parse variables
            for (var, val) in self.var_re.findall(line):
                if var in ignored_vars:
                    continue
                if var == 'Lang':
                    var = 'lang'
                    val = language_codes[val]
                vars[var] = val

        self.db.user_set_vars(user_id, vars)
        self.db.user_set_formula(user_id, formula)

        self.execute('finger %s' % usr, self.copy_notes, usr, tags, passwd,
            user_id, interface)

    def copy_notes(self, *args, **kwargs):
        (data, usr, tags, passwd, user_id, interface) = args
        lines = re.split(self.crlf, data)
        for line in lines:
            m = re.match(' ?(\d\d?): (.*)', line)
            if m:
                self.db.set_note(user_id, int(m.group(1)), m.group(2))
        self.finish_register(usr, tags, passwd, user_id, interface)

    title_re = re.compile(r'\((\w+)\)')
    def create_user(self, usr, tags, passwd):
        phash = bcrypt.hashpw(passwd, bcrypt.gensalt())
        real_name = usr
        email = '%s@fics' % usr
        admin_level = 10
        try:
            user_id = self.db.user_add(usr, email, phash, real_name,
                usr, admin_level)
        except MySQLdb.IntegrityError:
            self.tell(usr, 'Sorry, it appears you are already registered.  Contact wmahan if you need to reset your password.')
            return None

        if tags:
            if len(tags) == 1:
                self.tell(usr, "I see you have the %s title; I'll automatically transfer it to FatICS." % (tags[0]))
            else:
                self.tell(usr, "I see you have the following titles: %s.  I'll automatically transfer them to FatICS." % ', '.join(tags))
            for tag in tags:
                if tag != 'U':
                    self.db.grant_title(user_id, tag)

        return user_id

    def finish_register(self, usr, tags, passwd, user_id, interface):
        if not interface:
            self.tell(usr, "It looks like you aren't using an interface.  You can log in to FatICS using telnet.")
        elif good_interface_re.match(interface):
            self.tell(usr, '''I see that you're using "%s".  This interface is fully supported on FatICS.''')
        elif bad_interface_re.match(interface):
            self.tell(usr, '''I see that you're using "%s".  This interface is not yet supported on FatICS.  Please connect using telnet or a supported interface.''')
        else:
            self.tell(usr, '''I don't recognize your interface, "%s".  It may not be supported on FatICS.  You are welcome to try it, but if you have problems, please connect using telnet or a supported interface.''' % interface)

        self.tell(usr, 'Registration complete.  You can now log in at %s.  The password for %s is: %s' % (server_address, usr, passwd))

    def continue_register(self, *args, **kwargs):
        (data, usr, tags) = args
        if 'does not receive tells' in data:
            # there's nothing we can do
            return
        print 'data %s' % data
        assert('told' in data)

        passwd = self._make_passwd()
        user_id = self.create_user(usr, tags, passwd)
        print 'created user %d(%s)' % (user_id, usr)
        if user_id is not None:
            print('vars %s' % usr)
            self.execute('vars %s' % usr, self.copy_vars, usr, tags, passwd,
                user_id)

    def register(self, usr, args, tags):
        if False and '(U)' in tags:
            self.tell(usr, 'Only registered FICS players can register for FatICS.')
            return
        tags = self.title_re.findall(tags)
        for tag in tags:
            if tag not in known_titles:
                self.tell(usr, "Oops, I don't recognize your \"%s\" title.  I'm sorry; please inform wmahan." % tag)
                return
        time.sleep(2)
        assert(self.last_tell_time is None)
        self.last_tell_time = time.time()
        self.execute('t %s Welcome!  Copying your notes and variables to FatICS....' % usr, self.continue_register, usr, tags)

    # unregistered bots can't do qtells, and have a rate limit on tells
    time_between_tells = 2.01
    last_tell_time = None
    def tell(self, usr, msg):
        now = time.time()
        if self.last_tell_time and (now - self.last_tell_time <
                self.time_between_tells):
            print 'sleeping %f secs' % (self.time_between_tells -
                (now - self.last_tell_time))
            time.sleep(self.time_between_tells - (now - self.last_tell_time))
        self.last_tell_time = now
        self.send('t %s %s' % (usr, msg))

    def help(self, usr, args, tags):
        self.tell(usr, 'Please see my finger notes.')

    def quit(self, usr, args, tags):
        if usr in bot_admins:
            self.close()

bot = FBot()
bot.connect(username, password, host, port)

while True:
    bot.run()
    time.sleep(3)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
