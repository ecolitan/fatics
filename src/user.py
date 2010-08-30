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

import re
import bcrypt
import random
import string

import admin
import var
import channel
import notify
import connection
import rating
import speed_variant
from server import server
from db import db
from online import online
from config import config

class UsernameException(Exception):
    def __init__(self, reason):
        self.reason = reason

class BaseUser(object):
    def __init__(self):
        self.is_online = False
        self.notes = {}
        self._history = None
        self._titles = None
        self._title_str = None

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def log_on(self, conn):
        self.vars.update(var.varlist.get_transient_vars())
        self.aliases = {}
        self.formula = {}
        self.aliases = {}
        self.notifiers = set()
        self.censor = set()
        self.noplay = set()
        self.session = conn.session
        self.session.set_user(self)
        for ch in self.channels:
            channel.chlist[ch].log_on(self)
        notify.notify.users(self, _("Notification: %s has arrived.\n") % self.name)
        online.add(self)
        self.is_online = True
        self.write(_(server.get_copyright_notice()))

    def log_off(self):
        assert(self.is_online)
        for ch in self.channels:
            channel.chlist[ch].log_off(self)
        notify.notify.users(self, _("Notification: %s has departed.\n") % self.name)
        self.session.close()
        self.is_online = False
        online.remove(self)

    def write(self, s):
        assert(self.is_online)
        connection.written_users.add(self)
        self.session.conn.write(s)

    def send_prompt(self):
        assert(self.is_online)
        if self.session.ivars['defprompt']:
            self.session.conn.write(config.prompt)
        else:
            self.session.conn.write(self.vars['prompt'])

    def get_display_name(self):
        assert(self._title_str is not None)
        return '%s%s' % (self.name, self._title_str)

    def get_titles(self):
        assert(self._titles is not None)
        return self._titles

    def set_var(self, v, val):
        if val is not None:
            self.vars[v.name] = val
        else:
            if v.name in self.vars:
                del self.vars[v.name]

    def set_formula(self, v, val):
        if val is not None:
            self.formula[v.name] = val
        else:
            if v.name in self.formula:
                del self.formula[v.name]
    
    def set_note(self, v, val):
        num = int(v.name, 10)
        if val is not None:
            self.notes[num] = val
        else:
            if num in self.notes:
                del self.notes[num]
    
    def set_alias(self, name, val):
        if val is not None:
            self.aliases[name] = val
        else:
            del self.aliases[name]

    def add_channel(self, id):
        assert(type(id) == type(1) or type(id) == type(1l))
        self.channels.append(id)
        self.channels.sort()

    def remove_channel(self, id):
        assert(type(id) == type(1) or type(id) == type(1l))
        self.channels.remove(id)

    def set_admin_level(self, level):
        self.admin_level = level

    def add_notification(self, user):
        self.notifiers.add(user.name)

    def remove_notification(self, user):
        self.notifiers.remove(user.name)

    def add_censor(self, user):
        self.censor.add(user.name)

    def remove_censor(self, user):
        self.censor.remove(user.name)

    def add_noplay(self, user):
        self.noplay.add(user.name)

    def remove_noplay(self, user):
        self.noplay.remove(user.name)

    def send_board(self, game):
        self.write(game.variant.to_style12(self))

    def save_history(self, game_id, result_char, user_rating, color_char,
            opp_name, opp_rating, eco, flags, initial_time, inc,
            result_reason, when_ended):
        assert(self._history is not None)
        if len(self._history) == 0:
            num = 1
        else:
            num = (self._history[-1]['num'] + 1) % 100
            self._history = self._history[1:]
        entry = {'game_id': game_id, 'num': num, 'result_char': result_char,
            'user_rating': user_rating, 'color_char': color_char,
            'opp_name': opp_name, 'opp_rating': opp_rating, 'eco': eco,
            'flags' : flags, 'time': initial_time, 'inc' : inc,
            'result_reason': result_reason, 'when_ended': when_ended
        }
        self._history.append(entry)
        return entry

    def clear_history(self):
        self._history = []

    def has_timeseal(self):
        return self.session.use_timeseal or self.session.use_zipseal

# a registered user
class User(BaseUser):
    def __init__(self, u):
        BaseUser.__init__(self)
        self.id = u['user_id']
        self.name = u['user_name']
        self.passwd_hash = u['user_passwd']
        self.email = u['user_email']
        self.real_name = u['user_real_name']
        self.last_logout = u['user_last_logout']
        self.admin_level = u['user_admin_level']
        self.is_guest = False
        self.channels = db.user_get_channels(self.id)
        self.vars = db.user_get_vars(self.id)
        for f in db.user_get_formula(self.id):
            self.formula[f['num']] = f['f']
        for note in db.user_get_notes(self.id):
            self.notes[note['num']] = note['txt']
        self._rating = None

    def get_display_name(self):
        """Get the name displayed for other users, e.g. admin(*)(SR)"""
        if self._title_str is None:
            self._load_titles()
        return BaseUser.get_display_name(self)

    def _load_titles(self):
        disp_list = []
        self._titles = set()
        for t in db.user_get_titles(self.id):
            if t['display']:
                disp_list.append('(%s)' % t['title_flag'])
            self._titles.add(t['title_flag'])
        self._title_str = ''.join(disp_list)

    def log_on(self, conn):
        if online.is_online(self.name):
            conn.write(_("**** %s is already logged in; closing the other connection. ****\n" % self.name))
            u = online.find_exact(self.name)
            u.session.conn.write(_("**** %s has arrived; you can't both be logged in. ****\n\n") % self.name)
            #u.session.conn.write(_("**** %s has arrived - you can't both be logged in. ****\n\n") % self.name)
            u.session.conn.loseConnection('logged in again')
        BaseUser.log_on(self, conn)
        nlist = []
        for dbu in db.user_get_notifiers(self.id):
            name = dbu['user_name']
            if online.is_online(name):
                nlist.append(name)

            self.notifiers.add(dbu['user_name'])
        if len(nlist) > 0:
            self.write(_('Present company includes: %s\n') % ' '.join(nlist))

        for a in db.user_get_aliases(self.id):
            self.aliases[a['name']] = a['val']

        for dbu in db.user_get_censored(self.id):
            self.censor.add(dbu['user_name'])
        for dbu in db.user_get_noplayed(self.id):
            self.noplay.add(dbu['user_name'])

        self.get_history()

    def log_off(self):
        BaseUser.log_off(self)
        db.user_set_last_logout(self.id)

    def set_passwd(self, passwd):
        self.passwd_hash = bcrypt.hashpw(passwd, bcrypt.gensalt())
        db.user_set_passwd(self.id, self.passwd_hash)

    def set_admin_level(self, level):
        BaseUser.set_admin_level(self, level)
        db.user_set_admin_level(self.id, level)

    # check if an unencrypted password is correct
    def check_passwd(self, passwd):
        # don't perform expensive computation on arbitrarily long data
        if not is_legal_passwd(passwd):
            return False
        return bcrypt.hashpw(passwd, self.passwd_hash) == self.passwd_hash

    def get_last_logout(self):
        return db.user_get_last_logout(self.id)

    def remove(self):
        return db.user_delete(self.id)

    def set_var(self, v, val):
        BaseUser.set_var(self, v, val)
        if v.is_persistent:
            db.user_set_var(self.id, v.name, val)
    
    def set_formula(self, v, val):
        BaseUser.set_formula(self, v, val)
        db.user_set_formula(self.id, v.name, val)
    
    def set_note(self, v, val):
        BaseUser.set_note(self, v, val)
        db.user_set_note(self.id, v.name, val)
    
    def set_alias(self, name, val):
        BaseUser.set_alias(self, name, val)
        db.user_set_alias(self.id, name, val)

    def add_channel(self, id):
        BaseUser.add_channel(self, id)
        db.channel_add_user(id, self.id)

    def remove_channel(self, id):
        BaseUser.remove_channel(self, id)
        db.channel_del_user(id, self.id)

    def add_title(self, id):
        db.user_add_title(self.id, id)
        self._load_titles()

    def remove_title(self, id):
        db.user_del_title(self.id, id)
        self._load_titles()

    def add_notification(self, user):
        BaseUser.add_notification(self, user)
        if not user.is_guest:
            db.user_add_notification(self.id, user.id)

    def remove_notification(self, user):
        BaseUser.remove_notification(self, user)
        if not user.is_guest:
            db.user_del_notification(self.id, user.id)
    
    def add_censor(self, user):
        BaseUser.add_censor(self, user)
        if not user.is_guest:
            db.user_add_censor(self.id, user.id)

    def remove_censor(self, user):
        BaseUser.remove_censor(self, user)
        if not user.is_guest:
            db.user_del_censor(self.id, user.id)

    def add_noplay(self, user):
        BaseUser.add_noplay(self, user)
        if not user.is_guest:
            db.user_add_noplay(self.id, user.id)

    def remove_noplay(self, user):
        BaseUser.remove_noplay(self, user)
        if not user.is_guest:
            db.user_del_noplay(self.id, user.id)

    def get_history(self):
        if self._history is None:
            self._history = [e for e in db.user_get_history(self.id)]
        return self._history

    def get_titles(self):
        if self._titles is None:
            self._load_titles()
        return BaseUser.get_titles(self)

    def save_history(self, game_id, result_char, user_rating, color_char,
            opp_name, opp_rating, eco, flags, initial_time, inc,
            result_reason, when_ended):
        entry = BaseUser.save_history(self, game_id, result_char, user_rating,
            color_char, opp_name, opp_rating, eco, flags, initial_time, inc,
            result_reason, when_ended)
        db.user_add_history(entry, self.id)

    def clear_history(self):
        BaseUser.clear_history(self)
        db.user_del_history(self.id)

    def get_rating(self, speed_variant):
        if self._rating is None:
            self._load_ratings()
        if speed_variant in self._rating:
            return self._rating[speed_variant]
        else:
            return rating.NoRating(is_guest=False)

    def set_rating(self, speed_variant,
            rating, rd, volatility, win, loss, draw, ltime):
        db.user_set_rating(self.id, speed_variant.speed.id,
            speed_variant.variant.id, rating, rd, volatility, win, loss,
            draw, win + loss + draw, ltime)
        self._load_ratings() # TODO: don't reload all ratings

    def del_rating(self, sv):
        db.user_del_rating(self.id, sv.speed.id, sv.variant.id)
        if self._rating is not None and sv in self._rating:
            del self._rating[sv]

    def _load_ratings(self):
        self._rating = {}
        for row in db.user_get_all_ratings(self.id):
            sv = speed_variant.from_ids(row['speed_id'],
                row['variant_id'])
            self._rating[sv] = rating.Rating(row['rating'],
                row['rd'], row['volatility'], row['ltime'],
                row['win'], row['loss'], row['draw'], row['best'],
                row['when_best'])

class GuestUser(BaseUser):
    def __init__(self, name):
        BaseUser.__init__(self)
        self.is_guest = True
        if name is None:
            count = 0
            while True:
                self.name = 'Guest'
                for i in range(4):
                    self.name = self.name + random.choice(string.ascii_uppercase)
                if not online.is_online(self.name):
                    break
                count = count + 1
                if count > 3:
                    # should not happen
                    raise Exception('Unable to create a guest account!')
            self.autogenerated_name = True
        else:
            self.name = name
            self.autogenerated_name = False
        self.admin_level = admin.Level.user
        self.channels = channel.chlist.get_default_guest_channels()
        self.vars = var.varlist.get_default_vars()

    def log_on(self, conn):
        self._titles = set(['U'])
        self._title_str = '(U)'
        BaseUser.log_on(self, conn)
        self._history = []

    def get_history(self):
        assert(self._history is not None)
        return self._history

    def get_rating(self, speed_variant):
        return rating.NoRating(is_guest=True)

class AmbiguousException(Exception):
    def __init__(self, names):
        self.names = names

"""Various ways to look up a user."""
class Find(object):
    """Find a user, accepting only exact matches."""
    username_re = re.compile('^[a-zA-Z_]+$')
    def by_name_exact(self, name, min_len=config.min_login_name_len,online_only=False):
        if len(name) < min_len:
            raise UsernameException(_('Names should be at least %d characters long.  Try again.\n') % min_len)
        elif len(name) > 17:
            raise UsernameException(_('Names should be at most %d characters long.  Try again.\n') % 17)
        elif not self.username_re.match(name):
            raise UsernameException(_('Names should only consist of lower and upper case letters.  Try again.\n'))

        u = online.find_exact(name)
        if not u and not online_only:
            dbu = db.user_get(name)
            if dbu:
                u = User(dbu)
        return u

    """Find a user but allow the name to abbreviated if
    it is unambiguous; if the name is not an exact match, prefer
    online users to offline"""
    def by_prefix(self, name, online_only=False):
        u = None
        if len(name) >= config.min_login_name_len:
            u = self.by_name_exact(name, 2, online_only=online_only)
        if not u:
            ulist = online.find_part(name)
            if len(ulist) == 1:
                u = ulist[0]
            elif len(ulist) > 1:
                # when there are multiple matching users
                # online, don't bother searching for offline
                # users who also match
                raise AmbiguousException([u.name for u in ulist])
        if u and online_only:
            assert(u.is_online)
        if not u and not online_only:
            ulist = db.user_get_matching(name)
            if len(ulist) == 1:
                u = User(ulist[0])
            elif len(ulist) > 1:
                raise AmbiguousException([u['user_name'] for u in ulist])
        return u

    """Like by_prefix(), but writes an error message
    on failure."""
    def by_prefix_for_user(self, name, conn, min_len=0, online_only=False):
        u = None
        try:
            if len(name) < min_len:
                conn.write(_('You need to specify at least %d characters of the name.\n') % min_len)
            else:
                u = self.by_prefix(name, online_only=online_only)
                if online_only:
                    if not u:
                        conn.write(_('No user named "%s" is logged in.\n') % name)
                        u = None
                    else:
                        assert(u.is_online)
                elif not u:
                    conn.write(_('There is no player matching the name "%s".\n') % name)
        except UsernameException:
            conn.write(_('"%s" is not a valid handle.\n') % name)
        except AmbiguousException as e:
            conn.write("""Ambiguous name "%s". Matches: %s\n""" % (name, ' '.join(e.names)))
        return u

    """Like by_name_exact, but writes an error message
    on failure."""
    def by_name_exact_for_user(self, name, conn):
        u = None
        try:
            u = self.by_name_exact(name)
        except UsernameException:
            conn.write(_('"%s" is not a valid handle.\n') % name)
        else:
            if not u:
                conn.write(_('There is no player matching the name "%s".\n') % name)
        return u

find = Find()

# test whether a string meets the requirements for a password
def is_legal_passwd(passwd):
    if len(passwd) > 32:
        return False
    if len(passwd) < 3:
        return False
    # passwords may not contain spaces because they are set
    # using a command
    if not re.match(r'^\S+$', passwd):
        return False
    return True

class Create(object):
    def passwd(self):
        chars = string.letters + string.digits
        passlen = random.choice(range(5, 8))
        ret = ''
        for i in range(passlen):
            ret = ret + random.choice(chars)
        return ret

    def new(self, name, email, passwd, real_name):
        hash = bcrypt.hashpw(passwd, bcrypt.gensalt())
        db.user_add(name, email, hash, real_name, admin.Level.user)
create = Create()

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
