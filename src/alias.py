import re
#import curses.ascii

class AliasError(Exception):
        pass

class Alias(object):
        system = {
                'a': 'accept',
                'ame': 'allobservers $m',
                'answer': 'tell 1 (answering $1): $2-',
                'answer4': 'tell 4 (answering $1): $2-',
                'at': 'accept t $@',
                'b': 'backward $@',
                'bu': 'bugwho $@',
                'bug': 'bugwho $@',
                'bye': 'quit',
                'clearboard': 'bsetup',
                'Cls': 'help',
                'cm': 'clearmessages $@',
                'd': 'decline $@',
                'dt': 'decline t $@',
                'g': 'games $@',
                'e': 'examine $@',
                'exit': 'quit',
                'exl': 'examine $m -1',
                'f': 'finger $@',
                'fi': 'finger $@',
                'fo': 'forward $@',
                'fop': 'finger  $o $@',
                'fp': 'finger $p $@',
                'f.': 'finger $. $@',
                'gf': 'getgame $@',
                'gfm': 'getgame $@fm',
                'gm': 'getgame $@m',
                'got': 'goboard $@',
                'goto': 'goboard $@',
                'h': 'help $@',
                'hi': 'history $@',
                'ho': 'history $o',
                'hp': 'history $p',
                'hr': 'hrank $@',
                'in': 'inchannel $@',
                'i': 'it $@',
                'ivars': 'ivariables $@',
                'jl': 'jsave $1 $m -1',
                'lec': 'xtell lecturebot $@',
                'logout': 'quit',
                'm': 'match $@',
                'ma': 'match $@',
                'mailold': 'mailstored $@ -1',
                'mailoldme': 'mailstored $m -1',
                'mailoldmoves': 'mailstored $@ -1',
                'mam': 'xtell mamer! $@',
                'mb': 'xtell mailbot! $@',
                'more': 'next',
                'motd': 'help motd',
                'n': 'next $@',
                'new': 'news $@',
                'o': 'observe $@',
                'ol': 'smoves $@ -1',
                'old': 'smoves $@ -1',
                'oldme': 'smoves $m -1',
                'oldmoves': 'smoves $@ -1',
                'p': 'who a$@',
                'pl': 'who a$@',
                'player': 'who a$@',
                'players': 'who a$@',
                'q': '''tell $m The command 'quit' cannot be abbreviated.''',
                'qu': '''tell $m The command 'quit' cannot be abbreviated.''',
                'qui': '''tell $m The command 'quit' cannot be abbreviated.''',
                'r': 'refresh $@',
                're': 'refresh $@',
                'rem': 'rematch',
                'res': 'resign $@',
                #'rping': 'xtell ROBOadmin Ping',
                'saa': 'simallabort',
                'saab': 'simallabort',
                'saadj': 'simalladjourn',
                'sab': 'simabort $@',
                'sadj': 'simadjourn $@',
                'setup': 'bsetup $@',
                'sh': 'shout $@',
                'sn': 'simnext',
                'sp': 'simprev',
                'sping': 'ping $1',
                'stats': 'statistics $@',
                't': 'tell $@',
                'td': 'xtell SuperTD $@',
                'vars': 'variables $@',
                'w': 'who $@',
                'worst': 'rank 0 $1',
                'wt': 'withdraw t $@',
                'ungetgame': 'unseek',
                'znotl': 'znotify $@',
                '.': 'tell . $@',
                ',': 'tell , $@',
                '`': 'tell . $@',
                '!': 'shout $@',
                ':': 'it $@',
                '^': 'cshout $@',
                '?': 'help $@',
                '*': 'kibitz $@',
                '#': 'whisper $@',
                '+': 'addlist $@',
                '-': 'sublist $@',
                '=': 'showlist $@',
                'p+': 'ptell p+ $@',
                'p++': 'ptell p++ $@',
                'p+++': 'ptell p+++ $@',
                'p-': 'ptell p- $@',
                'p--': 'ptell p-- $@',
                'p---': 'ptell p--- $@',
                'n+': 'ptell n+ $@',
                'n++': 'ptell n++ $@',
                'n+++': 'ptell n+++ $@',
                'n-': 'ptell n- $@',
                'n--': 'ptell n-- $@',
                'n---': 'ptell n--- $@',
                'b+': 'ptell b+ $@',
                'b++': 'ptell b++ $@',
                'b+++': 'ptell b+++ $@',
                'b-': 'ptell b- $@',
                'b--': 'ptell b-- $@',
                'b---': 'ptell b--- $@',
                'r+': 'ptell r+ $@',
                'r++': 'ptell r++ $@',
                'r+++': 'ptell r+++ $@',
                'r-': 'ptell r- $@',
                'r--': 'ptell r-- $@',
                'r---': 'ptell r--- $@',
                'q+': 'ptell q+ $@',
                'q++': 'ptell q++ $@',
                'q+++': 'ptell q+++ $@',
                'q-': 'ptell q- $@',
                'q--': 'ptell q-- $@',
                'q---': 'ptell q--- $@',
                'h+': 'ptell h+ $@',
                'h++': 'ptell h++ $@',
                'h+++': 'ptell h+++ $@',
                'h-': 'ptell h- $@',
                'h--': 'ptell h-- $@',
                'h---': 'ptell h--- $@',
                'd+': 'ptell d+ $@',
                'd++': 'ptell d++ $@',
                'd+++': 'ptell d+++ $@',
                'd-': 'ptell d- $@',
                'd--': 'ptell d-- $@',
                'd---': 'ptell d--- $@',
                'sit': 'ptell sit! $@',
                'nosit': 'ptell go! $@',
                'mateme': 'ptell $1 mates me! $@',
                'mates': 'ptell $1 mates $o! $@'
        }

        """Expand system and user aliases in a given command."""
        def expand(self, s, syslist, userlist, user):
                m = re.match(r'''^([@!#$%^&*\-+'"\/.,=]+)(.*)''', s)
                if m:
                        word = m.group(1)
                        rest = m.group(2)
                else:
                        m = re.match(r'^(\S+)(?:\s+(.*))?$', s)
                        if m:
                                word = m.group(1)
                                rest = m.group(2)

                if m:
                        if word in userlist:
                                s = self._expand_params(userlist[word], rest, user)
                        elif word in syslist:
                                s = self._expand_params(syslist[word], rest, user)
                return s

        def _expand_params(self, alias_str, rest, user):
                # unlike lasker, but like FICS, there is no implicit
                # $@ after simple aliases
                assert(alias_str != None)
                if rest == None:
                        rest = ''
                rest_split = None
                ret = ''
                i = 0
                aliaslen = len(alias_str)
                while i < aliaslen:
                        if alias_str[i] == '$':
                                i += 1
                                # raises an error if beyond the end
                                char = alias_str[i]
                                if char == '@':
                                        ret += rest if rest != None else ''
                                elif char == '-':
                                        if i < aliaslen - 1 and re.match('[0-9]', alias_str[i + 1]):
                                                # $-n
                                                i += 1
                                                if rest_split == None:
                                                        rest_split = re.split('\s+', rest)
                                                d = int(char, 10) - 1
                                                ret += ' '.join(rest_split[:d])
                                        else:
                                                ret += '-'
                                elif re.match('[0-9]', char):
                                        if rest_split == None:
                                                rest_split = re.split('\s+', rest)
                                        d = int(char, 10) - 1
                                        if i < aliaslen - 1 and alias_str[i + 1] == '-':
                                                # $n-
                                                i += 1
                                                ret += ' '.join(rest_split[d:])
                                        else:
                                                # $n
                                                try:
                                                        ret += rest_split[d]
                                                except IndexError:
                                                        # not fatal since parameters can be optional
                                                        pass
                                elif char == 'm':
                                        ret += user.name
                                elif char == 'o':
                                        # XXX
                                        pass
                                elif char == 'p':
                                        # XXX
                                        pass
                                elif char == '.':
                                        if user.last_tell_user == None:
                                                raise AliasError()
                                        ret += user.last_tell_user.name
                                elif char == ',':
                                        if user.last_tell_ch == None:
                                                raise AliasError()
                                        ret += '%s' % user.last_tell_ch
                                elif char == '$':
                                        ret += '$'
                                else:
                                        # unrecognized $ variable
                                        raise AliasError()
                        else:
                                ret += alias_str[i]
                        i += 1

                #print 'expanded to %s' % ret
                return ret

alias = Alias()

# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent
