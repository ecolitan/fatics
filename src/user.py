import re
import bcrypt
import random
import string

import admin
import var
import channel
import notify
from db import db
from online import online
from config import config

class UsernameException(Exception):
    def __init__(self, reason):
        self.reason = reason

class BaseUser(object):
    def __init__(self):
        self.is_online = False
        self.ivars = var.varlist.get_default_ivars()
        self.notes = {}
        self.aliases = {}

    def __eq__(self, other):
        return self.name == other.name

    def log_on(self, conn):
        if not self.is_guest:
            if online.is_online(self.name):
                conn.write(_("**** %s is already logged in; closing the other connection. ****\n" % self.name))
                u = online.find_exact(self.name)
                u.session.conn.write(_("**** %s has arrived; you can't both be logged in. ****\n\n") % self.name)
                #u.session.conn.write(_("**** %s has arrived - you can't both be logged in. ****\n\n") % self.name)
                u.session.conn.loseConnection('logged in again')
        self.vars.update(var.varlist.get_transient_vars())
        self.aliases = {}
        self.formula = {}
        self.session = conn.session
        self.session.set_user(self)
        for ch in self.channels:
            channel.chlist[ch].log_on(self)
        online.add(self)
        self.is_online = True
        conn.write(_('**** Starting OICS session as %s ****\n\n') % self.name)

    def log_off(self):
        for ch in self.channels:
            channel.chlist[ch].log_off(self)
        self.session.close()
        self.is_online = False
        online.remove(self)

    def write(self, s):
        assert(self.is_online)
        self.session.conn.write(s)

    def write_prompt(self, s):
        assert(self.is_online)
        self.session.conn.write(s)
        self.session.conn.write('fics% ')

    def get_display_name(self):
        return self.name + self.title_str

    def set_var(self, v, val):
        var_dict = self.ivars if v.is_ivar else self.vars
        if val != None:
            var_dict[v.name] = val
        else:
            if v.name in var_dict:
                del var_dict[v.name]
    
    def set_formula(self, v, val):
        if val != None:
            self.formula[v.name] = val
        else:
            if v.name in self.formula:
                del self.formula[v.name]
    
    def set_note(self, v, val):
        num = int(v.name, 10)
        if val != None:
            self.notes[num] = val
        else:
            if num in self.notes:
                del self.notes[num]
    
    def set_alias(self, name, val):
        if val != None:
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

    def get_rating(self, variant):
        if self.is_guest:
            return '++++'
        else:
            return '----'
    
    def send_board(self, vari):
        self.write(vari.to_style12(self))

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
        self._make_title_str()

    def _make_title_str(self):
        self.title_str = ''
        titles =  db.user_get_titles(self.id)
        for title in titles:
            if title['display']:
                self.title_str += '(%s)' % title['title_flag']

    def log_on(self, conn):
        BaseUser.log_on(self, conn)
        notify.notify.users(self.id, _("Notification: %s has arrived.\n") % self.name)
        notifiers = db.user_get_notifiers(self.id)
        notifiers = [dbu['user_name'] for dbu in notifiers if online.is_online(dbu['user_name'])]
        if len(notifiers) > 0:
            self.write(_('Present company includes: %s\n') % ' '.join(notifiers))
        for a in db.user_get_aliases(self.id):
            self.aliases[a['name']] = a['val']

    def log_off(self):
        BaseUser.log_off(self)
        notify.notify.users(self.id, _("Notification: %s has departed.\n") % self.name)
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
        self._make_title_str()

    def remove_title(self, id):
        db.user_del_title(self.id, id)
        self._make_title_str()

    def add_notification(self, user):
        db.user_add_notification(self.id, user.id)

    def remove_notification(self, user):
        db.user_del_notification(self.id, user.id)

class GuestUser(BaseUser):
    def __init__(self, name):
        BaseUser.__init__(self)
        self.is_guest = True
        if name == None:
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
        self.title_str = '(U)'

    def log_on(self, conn):
        BaseUser.log_on(self, conn)
    
class AmbiguousException(Exception):
    def __init__(self, names):
        self.names = names

"""Various ways to look up a user."""
class Find(object):
    """Find a user, accepting only exact matches."""
    def by_name_exact(self, name, min_len=config.min_login_name_len,online_only=False):
        if len(name) < min_len:
            raise UsernameException(_('Names should be at least %d characters long.  Try again.\n') % min_len)
        elif len(name) > 18:
            raise UsernameException(_('Names should be at most %d characters long.  Try again.\n') % 18)
        elif not re.match('^[a-zA-Z_]+$', name):
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
    def by_name_or_prefix(self, name, online_only=False):
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

    """Like by_name_or_prefix(), but writes an error message
    on failure."""
    def by_name_or_prefix_for_user(self, name, conn, min_len=0, online_only=False):
        u = None
        try:
            if len(name) < min_len:
                conn.write(_('You need to specify at least %d characters of the name.\n') % min_len)
            else:
                u = self.by_name_or_prefix(name, online_only=online_only)
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
            conn.write(_('"%s" is not a valid handle\n.') % name)
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
