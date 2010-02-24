import trie
import channel

lists = trie.Trie()

class MyList(object):
        def __init__(self, name):
                lists[name] = self

class SysList(MyList):
        pass

class AdminList(MyList):
        pass

class UserList(MyList):
        pass

class ListError(Exception):
        def __init__(self, reason):
                self.reason = reason

class ChannelList(UserList):
        def __init__(self):
                MyList.__init__(self, "channel")

        def add(self, val, user):
                try:
                        val = int(val, 10)
                        channel.chlist[val].add(user)
                except ValueError:
                        raise ListError(_('The channel must be a number.'))
                except KeyError:
                        raise ListError(_('Invalid channel number.'))

        def sub(self, val, user):
                try:
                        val = int(val, 10)
                        channel.chlist[val].remove(user)
                except ValueError:
                        raise ListError(_('The channel must be a number.'))
                except KeyError:
                        raise ListError(_('Invalid channel number.'))

ChannelList()

# admin removedcom filter ban abuser muzzle, cmuzzle, c1muzzle, c24muzzle, c46muzzle, c49muzzle, c50muzzle, c51muzzle, fm, im, gm, wgm, blind, teams, computer, td, censor, gnotify, noplay, channel, follow, remote
# ca, sr, idlenotify, mamermgr, wfm

"""a list of lists"""
"""class ListList(object):
        def __init__(self):
                UserList("channel", 
listlist = ListList()"""

# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent
