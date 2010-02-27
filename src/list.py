import trie
import channel

lists = trie.Trie()

class MyList(object):
        #[perm_head, perm_god, perm_admin, perm_public, perm_personal] = range(5)
        def __init__(self, name):
                lists[name] = self

class ListError(Exception):
        def __init__(self, reason):
                self.reason = reason

class TitleList(MyList):
        def __init__(self, name):
                MyList.__init__(self, name)
                self.members = []

        def add(self, args, user):
                if user.admin_level < admin.level.admin:
                        raise ListError(_("You don't have permission to do that."))
                self.members.append(args[1])
                
        def show(self, args, user):
                user.write('%s: ' % self.name.upper())

        def sub(self, val, user):
                if user.admin_level < admin.level.admin:
                        raise ListError(_("You don't have permission to do that."))
                try:
                        self.members.remove(user.name)
                except KeyError:
                        raise ListError(_("%s is not in the %s list.") % (user.name, self.name.upper()))

class ChannelList(MyList):
        def add(self, args, user):
                try:
                        val = int(args[1], 10)
                        channel.chlist[val].add(user)
                except ValueError:
                        raise ListError(_('The channel must be a number.'))
                except KeyError:
                        raise ListError(_('Invalid channel number.'))


        def sub(self, args, user):
                try:
                        val = int(args[1], 10)
                        channel.chlist[val].remove(user)
                except ValueError:
                        raise ListError(_('The channel must be a number.'))
                except KeyError:
                        raise ListError(_('Invalid channel number.'))

"""a list of lists"""
class ListList(object):
        def __init__(self):
                ChannelList("channel")
                
                TitleList("wfm")
                TitleList("fm") 
                TitleList("wim") 
                TitleList("im") 
                TitleList("wgm")
                TitleList("gm")
        
ListList()

# admin removedcom filter ban abuser muzzle, cmuzzle, c1muzzle, c24muzzle, c46muzzle, c49muzzle, c50muzzle, c51muzzle, fm, im, gm, wgm, blind, teams, computer, td, censor, gnotify, noplay, channel, follow, remote
# ca, sr, idlenotify, mamermgr, wfm

'''
{{P_HEAD, "admin"},
 {P_GOD, "removedcom"},
 {P_ADMIN, "filter"},
 {P_ADMIN, "ban"},
 {P_ADMIN, "abuser"},
 {P_ADMIN, "muzzle"},
 {P_ADMIN, "cmuzzle"},
 {P_ADMIN, "c1muzzle"}, /* possible FICS trouble spots */
 {P_ADMIN, "c24muzzle"}, /* would prefer two param addlist - DAV */
 {P_ADMIN, "c46muzzle"}, /* is a temp solution */
 {P_ADMIN, "c49muzzle"},
 {P_ADMIN, "c50muzzle"},
 {P_ADMIN, "c51muzzle"},
 {P_PUBLIC, "fm"},
 {P_PUBLIC, "im"},
 {P_PUBLIC, "gm"},
 {P_PUBLIC, "wgm"},
 {P_PUBLIC, "blind"},
 {P_PUBLIC, "teams"},
 {P_PUBLIC, "computer"},
 {P_PUBLIC, "td"},
 {P_PERSONAL, "censor"},
 {P_PERSONAL, "gnotify"},
 {P_PERSONAL, "noplay"},
 {P_PERSONAL, "notify"},
 {P_PERSONAL, "channel"},
 {P_PERSONAL, "follow"},
 {P_PERSONAL, "remote"},
 '''

# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent
