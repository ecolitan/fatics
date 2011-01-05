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
import datetime
import pytz

import admin
import var
import channel
import notify
import connection
import rating
import speed_variant
import lang

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
        self.notifiers = set()
        self.notified = set()
        self.gnotifiers = set()
        self.gnotified = set()
        self.noplay = set()
        self.session = conn.session
        self.session.set_user(self)
        db.user_log(self.name, login=True, ip=conn.ip)
        self.is_online = True
        online.add(self)
        self.write(server.get_copyright_notice())
        self.write(db.get_server_message('motd'))
        for ch in self.channels:
            channel.chlist[ch].log_on(self)

    def log_off(self):
        assert(self.is_online)

        db.user_log(self.name, login=False, ip=self.session.conn.ip)

        for ch in self.channels:
            channel.chlist[ch].log_off(self)
        self.session.close()
        self.is_online = False
        online.remove(self)

    def write(self, s):
        assert(self.is_online)
        connection.written_users.add(self)
        self.session.conn.write(s)

    # Like write(), but localizes for this user.
    def write_(self, s, args={}):
        #assert(isinstance(args, (list, dict, tuple)))
        connection.written_users.add(self)
        self.session.conn.write(lang.langs[self.vars['lang']].gettext(s) %
            args)

    def nwrite_(self, s1, s2, n, args={}):
        connection.written_users.add(self)
        self.session.conn.write(
            lang.langs[self.vars['lang']].ngettext(s1, s2, n) % args)

    def translate(self, s, args={}):
        return lang.langs[self.vars['lang']].gettext(s) % args

    def send_prompt(self):
        assert(self.is_online)
        if self.session.ivars['defprompt']:
            self.session.conn.write(config.prompt)
        else:
            self.session.conn.write(self.vars['prompt'])

    def get_display_name(self):
        assert(self._title_str is not None)
        return '%s%s' % (self.name, self._title_str)

    def __str__(self):
        return self.name

    def has_title(self, title):
        assert(self._titles is not None)
        return title in self._titles

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
            self.vars[v.name] = val
        else:
            if v.name in self.vars:
                del self.vars[v.name]

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

    def is_admin(self):
        return self.admin_level >= admin.Level.admin

    def add_notification(self, user):
        self.notifiers.add(user.name)
        if user.is_online:
            user.notified.add(self.name)

    def remove_notification(self, user):
        self.notifiers.remove(user.name)
        if user.is_online:
            user.notified.remove(self.name)

    def add_gnotification(self, user):
        self.gnotifiers.add(user.name)
        if user.is_online:
            user.gnotified.add(self.name)

    def remove_gnotification(self, user):
        self.gnotifiers.remove(user.name)
        if user.is_online:
            user.gnotified.remove(self.name)

    def add_idlenotification(self, user):
        """ Inform this user when the given user unidles. """
        assert(self.is_online)
        assert(user.is_online)
        self.session.idlenotifying.add(user)
        user.session.idlenotified_by.add(self)

    def remove_idlenotification(self, user):
        """ Remove a notification added by add_idlenotification. """
        assert(self.is_online)
        assert(user.is_online)
        self.session.idlenotifying.remove(user)
        user.session.idlenotified_by.remove(self)

    def add_censor(self, user):
        self.censor.add(user.name)

    def remove_censor(self, user):
        self.censor.remove(user.name)

    def add_noplay(self, user):
        self.noplay.add(user.name)

    def remove_noplay(self, user):
        self.noplay.remove(user.name)

    def censor_or_noplay(self, b):
        """ Check whether either player censors or noplays the other, without
        printing any messages to the users. """
        a = self
        return (a.name in b.censor or a.name in b.noplay
            or b.name in a.censor or b.name in a.noplay)

    def save_history(self, game_id, result_char, user_rating, color_char,
            opp_name, opp_rating, eco, flags, initial_time, inc,
            result_reason, when_ended, movetext, idn):
        assert(self._history is not None)
        if len(self._history) == 0:
            num = 0
        else:
            num = (self._history[-1]['num'] + 1) % 100
            if len(self._history) == 10:
                self._history = self._history[1:]
        entry = {'game_id': game_id, 'num': num, 'result_char': result_char,
            'user_rating': user_rating, 'color_char': color_char,
            'opp_name': opp_name, 'opp_rating': opp_rating, 'eco': eco,
            'flags' : flags, 'time': initial_time, 'inc' : inc,
            'result_reason': result_reason, 'when_ended': when_ended,
            'movetext': movetext, 'idn': idn
        }
        self._history.append(entry)
        return entry

    def clear_history(self):
        self._history = []

    def get_history_game(self, num, conn):
        hist = self.get_history()
        if not hist:
            conn.write(_('%s has no history games.\n') % self.name)
        h = None
        if num < 0:
            if num < -10:
                conn.write(_('There are 10 entries maximum in history.\n'))
                return
            try:
                h = hist[num]
            except IndexError:
                pass
        else:
            matches = [h for h in hist if h['num'] == num]
            assert(len(matches) in [0, 1])
            h = matches[0] if matches else None

        if h:
            assert(h['color_char'] in ['W', 'B'])
            if h['color_char'] == 'W':
                h['white_name'] = self.name
                h['black_name'] = h['opp_name']
                if h['result_char'] == '+':
                    h['result'] = '1-0'
                elif h['result_char'] == '-':
                    h['result'] = '0-1'
                elif h['result_char'] == '=':
                    h['result'] = '1/2-1/2'
                elif h['result_char'] == '*':
                    h['result'] = '*'
                else:
                    raise RuntimeError('unknown result char %s' % result_char)
            else:
                h['white_name'] = h['opp_name']
                h['black_name'] = self.name
                if h['result_char'] == '+':
                    h['result'] = '0-1'
                elif h['result_char'] == '-':
                    h['result'] = '1-0'
                elif h['result_char'] == '=':
                    h['result'] = '1/2-1/2'
                elif h['result_char'] == '*':
                    h['result'] = '*'
                else:
                    raise RuntimeError('unknown result char %s' % result_char)
        else:
            conn.write(_('There is no history game %(num)d for %(name)s.\n') % {'num': num, 'name': self.name})

        return h

    def has_timeseal(self):
        return self.session.use_timeseal or self.session.use_zipseal

    def in_silence(self):
        return self.vars['silence'] and (self.session.game
            or self.session.observed)

    def hears_channels(self):
        return not self.vars['chanoff'] and not self.in_silence()

    def format_datetime(self, dt):
        return dt.replace(tzinfo=pytz.utc).strftime("%Y-%m-%d %H:%M %Z")
        #return dt.strftime("%a %b %e, %H:%M %Z %Y")

    def set_muted(self, val):
        """ Mute or unmute the user (affects all communications). """
        self.is_muted = val

    def set_playbanned(self, val):
        self.is_playbanned = val

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
        self.is_banned = u['user_banned']
        self.is_ratedbanned = u['user_ratedbanned']
        self.is_playbanned = u['user_playbanned']
        self.is_muzzled = u['user_muzzled']
        self.is_muted = u['user_muted']
        self.is_guest = False
        self.channels = db.user_get_channels(self.id)
        self.vars = db.user_get_vars(self.id,
            var.varlist.get_persistent_var_names())

        self.vars['formula'] = None
        for num in range(1, 10):
            self.vars['f' + str(num)] = None

        for f in db.user_get_formula(self.id):
            #self.formula[f['num']] = f['f']
            if f['num'] == 0:
                self.vars['formula'] = f['f']
            else:
                self.vars['f' + str(f['num'])] = f['f']
        for note in db.user_get_notes(self.id):
            self.notes[note['num']] = note['txt']
        self._rating = None
        self.tz = pytz.timezone(self.vars['tzone'])

    def _get_censor(self):
        if self._censor is None:
            self._censor = set([dbu['user_name'] for dbu in
                db.user_get_censored(self.id)])
        return self._censor
    _censor = None
    censor = property(fget=_get_censor)

    def get_display_name(self):
        """Get the name displayed for other users, e.g. admin(*)(SR)"""
        if self._title_str is None:
            self._load_titles()
        return BaseUser.get_display_name(self)

    def _load_titles(self):
        disp_list = []
        self._titles = set()
        for t in db.user_get_titles(self.id):
            if t['title_flag'] and t['title_light']:
                disp_list.append('(%s)' % t['title_flag'])
            self._titles.add(t['title_name'])
        self._title_str = ''.join(disp_list)

    def toggle_light(self, title_id):
        db.toggle_title_light(self.id, title_id)
        self._load_titles()

    def log_on(self, conn):
        if online.is_online(self.name):
            conn.write(_("**** %s is already logged in; closing the other connection. ****\n" % self.name))
            u = online.find_exact(self.name)
            u.session.conn.write(_("**** %s has arrived; you can't both be logged in. ****\n\n") % self.name)
            #u.session.conn.write(_("**** %s has arrived - you can't both be logged in. ****\n\n") % self.name)
            u.session.conn.loseConnection('logged in again')

        BaseUser.log_on(self, conn)

        news = db.get_news_since(self.last_logout, is_admin=False)
        if news:
            conn.write(ngettext('There is %d new news item since your last login:\n',
                'There are %d new news items since your last login:\n', len(news))
                % len(news))
            for item in reversed(news):
                conn.write('%4d (%s) %s\n' % (item['news_id'],
                    item['news_date'], item['news_title']))
        else:
            conn.write(_('There are no new news items.\n'))
        conn.write('\n')

        (mcount, ucount) = db.get_message_count(self.id)
        assert(mcount >= 0)
        assert(ucount >= 0)
        conn.write(ngettext('You have %(mcount)d message (%(ucount)d unread).\n',
            'You have %(mcount)d messages (%(ucount)d unread).\n', mcount) %
            {'mcount': mcount, 'ucount': ucount})
        conn.write(_('Use "messages u" to view unread messages and "clearmessages *" to clear all.\n'))

        for dbu in db.user_get_notified(self.id):
            name = dbu['user_name']
            self.notified.add(name)

        nlist = []
        for dbu in db.user_get_notifiers(self.id):
            name = dbu['user_name']
            self.notifiers.add(name)
            if online.is_online(name):
                nlist.append(name)
        notify.notify_users(self, arrived=True)

        if nlist:
            self.write(_('Present company includes: %s\n') % ' '.join(nlist))

        # gnotify
        self.gnotifiers = set([dbu['user_name']
            for dbu in db.user_get_gnotifiers(self.id)])
        self.gnotified = set([dbu['user_name']
            for dbu in db.user_get_gnotified(self.id)])

        for a in db.user_get_aliases(self.id):
            self.aliases[a['name']] = a['val']

        #for dbu in db.user_get_censored(self.id):
        #    self.censor.add(dbu['user_name'])
        for dbu in db.user_get_noplayed(self.id):
            self.noplay.add(dbu['user_name'])

        self.get_history()

    def log_off(self):
        notify.notify_users(self, arrived=False)
        BaseUser.log_off(self)
        db.user_set_last_logout(self.id)

    def get_log(self):
        return db.user_get_log(self.name)

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

    def add_channel(self, chid):
        BaseUser.add_channel(self, chid)
        db.channel_add_user(chid, self.id)

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

    def add_gnotification(self, user):
        BaseUser.add_gnotification(self, user)
        if not user.is_guest:
            db.user_add_gnotification(self.id, user.id)

    def remove_gnotification(self, user):
        BaseUser.remove_gnotification(self, user)
        if not user.is_guest:
            db.user_del_gnotification(self.id, user.id)

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

    def has_title(self, title):
        if self._titles is None:
            self._load_titles()
        return BaseUser.has_title(self, title)

    def get_titles(self):
        if self._titles is None:
            self._load_titles()
        return BaseUser.get_titles(self)

    def save_history(self, game_id, result_char, user_rating, color_char,
            opp_name, opp_rating, eco, flags, initial_time, inc,
            result_reason, when_ended, movetext, idn):
        entry = BaseUser.save_history(self, game_id, result_char, user_rating,
            color_char, opp_name, opp_rating, eco, flags, initial_time, inc,
            result_reason, when_ended, movetext, idn)
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

    def set_email(self, email):
        db.user_set_email(self.id, email)
        self.email = email

    def set_banned(self, val):
        """ Ban or unban this user. """
        self.is_banned = val
        db.user_set_banned(self.id, 1 if val else 0)

    def set_muzzled(self, val):
        """ Muzzle or unmuzzle the user (affects shouts). """
        self.is_muzzled = val
        db.user_set_muzzled(self.id, 1 if val else 0)

    def set_muted(self, val):
        BaseUser.set_muted(self, val)
        db.user_set_muted(self.id, 1 if val else 0)

    def set_ratedbanned(self, val):
        """ Add or remove this user from the ratedban list. """
        self.is_ratedbanned = val
        db.user_set_ratedbanned(self.id, 1 if val else 0)

    def set_playbanned(self, val):
        BaseUser.set_playbanned(self, val)
        db.user_set_playbanned(self.id, 1 if val else 0)

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
        self.censor = set()
        self.is_muted = False
        self.is_playbanned = False
        self.tz = pytz.timezone(self.vars['tzone'])

    def log_on(self, conn):
        self._titles = set(['unregistered'])
        self._title_str = '(U)'
        BaseUser.log_on(self, conn)
        self._history = []

    def get_log(self):
        """ The log for a guest has just one entry: the login """
        return [{'log_who_name': self.name,
            'log_when': datetime.datetime.fromtimestamp(self.session.login_time),
            'log_which': 'login', 'log_ip': self.session.conn.ip}]
        db.user_get_log(self.id)

    def get_history(self):
        assert(self._history is not None)
        return self._history

    def get_rating(self, speed_variant):
        return rating.NoRating(is_guest=True)

class AmbiguousException(Exception):
    def __init__(self, names):
        self.names = names

def _check_name(name, min_len):
    """ Check whether a string is a valid user name. """
    if len(name) < min_len:
        raise UsernameException(_('Names should be at least %d characters long.  Try again.\n') % min_len)
    elif len(name) > 17:
        raise UsernameException(_('Names should be at most %d characters long.  Try again.\n') % 17)
    elif not username_re.match(name):
        raise UsernameException(_('Names should only consist of lower and upper case letters.  Try again.\n'))

username_re = re.compile('^[a-zA-Z_]+$')
def find_by_name_exact(name,
        min_len=config.min_login_name_len, online_only=False):
    """Find a user, accepting only exact matches. """
    _check_name(name, min_len)
    u = online.find_exact(name)
    if not u and not online_only:
        dbu = db.user_get(name)
        if dbu:
            u = User(dbu)
    return u

def _find_by_prefix(name, online_only=False):
    """ Find a user but allow the name to abbreviated if
    it is unambiguous; if the name is not an exact match, prefer
    online users to offline. """
    u = None

    # first try an exact match
    if len(name) >= config.min_login_name_len:
        u = find_by_name_exact(name, min_len=2, online_only=online_only)
    else:
        _check_name(name, 1)
    if not u:
        # failing that, try a prefix match
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

def find_by_prefix_for_user(name, conn, min_len=0, online_only=False):
    """ Like _find_by_prefix(), but writes a friendly error message on
    failure. """

    u = None
    try:
        # Original FICS interprets a name ending with ! as an exact name
        # that is not an abbreviation.  I don't see this documented anywhere
        # but Babas uses this for private tells.
        if name.endswith('!'):
            name = name[:-1]
            assert(len(name) > 0)
            return find_by_name_exact_for_user(name, conn,
                min_len=min_len, online_only=online_only)

        if len(name) < min_len:
            conn.write(_('You need to specify at least %d characters of the name.\n') % min_len)
        else:
            u = _find_by_prefix(name, online_only=online_only)
            if online_only:
                if not u:
                    conn.write(_('No player named "%s" is online.\n') % name)
                    u = None
                else:
                    assert(u.is_online)
            elif not u:
                conn.write(_('There is no player matching the name "%s".\n') % name)
    except UsernameException:
        conn.write(_('"%s" is not a valid handle.\n') % name)
    except AmbiguousException as e:
        conn.write(_("""Ambiguous name "%s". Matches: %s\n""") %
            (name, ' '.join(e.names)))
    return u

def find_by_name_exact_for_user(name, conn, min_len=config.min_login_name_len,
        online_only=False):
    """ Like find_by_name_exact, but writes an error message
    on failure. """
    u = None
    try:
        u = find_by_name_exact(name, min_len=min_len, online_only=online_only)
    except UsernameException:
        conn.write(_('"%s" is not a valid handle.\n') % name)
    else:
        if not u:
            conn.write(_('There is no player matching the name "%s".\n') % name)
    return u

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

def make_passwd():
    chars = string.letters + string.digits
    passlen = random.choice(range(5, 8))
    ret = ''
    for i in range(passlen):
        ret = ret + random.choice(chars)
    return ret

def add_user(name, email, passwd, real_name):
    pwhash = bcrypt.hashpw(passwd, bcrypt.gensalt())
    user_id = db.user_add(name, email, pwhash, real_name, admin.Level.user)
    for chid in channel.chlist.get_default_channels():
        db.channel_add_user(chid, user_id)
    return user_id

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
