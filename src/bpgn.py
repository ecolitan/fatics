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

# At present this is only used for tests.

import re
import copy

# XXX we ignore additional tags on the same line
tag_re = re.compile(r'''\[(\w+)\s+"([^"\n]*?)"\]\s*''')
space_re = re.compile(r'''\s+''')
move_num_re = re.compile(r'''(\d+)([AaBb])\.*''')
move_re = re.compile(r'''([NBRQK]?[a-h1-8x]{2,5}(?:=[NBRQK])?|[PNBRQpnbrq]@[a-h][1-8]|O-O-O|O-O)([+#])?''')
dots_re = re.compile(r'''\.\.\.''')
comment_re = re.compile(r'''\{(.*?)\}''', re.S)
nag_re = re.compile(r'''\$(\d+)''')
result_re = re.compile(r'''(1-0|0-1|1/2-1/2|\*)''')
checkmate_re = re.compile(r'''(\w+)\s+checkmated\s*$''')
#resign_re = re.compile(r'''(\w+)\s+resigns\s*$''')
#partner_won_re = re.compile(r'''(\w+)'s\s+partner\s+won\*$''')
stalemate_re = re.compile(r'''\s+drawn\s+by\s+stalemate\s*$''')
repetition_re = re.compile(r'''\s+drawn\s+by\s+repetition\s*$''')
fifty_re = re.compile(r'''\s+drawn\s+by\s+the\s+50\s+move\s+rule\s*$''')

class PgnError(Exception):
    def __init__(self, reason):
        self.reason = reason
        print reason

class BpgnMove(object):
    def __init__(self, text, decorator, char):
        self.text = text
        self.decorator = decorator if decorator is not None else ''
        self.char = char
        self.comments = []

    def add_comment(self, com):
        self.comments.append(com)

class Bpgn(object):
    def __init__(self, f):
        self.f = f

    def __iter__(self):
        skip_blank = True
        line_num = 0
        tags = {}
        in_tag_section = True

        for line in self.f:
            line = line.rstrip('\r\n')
            if skip_blank:
                if line == '' or line[0:6] == '{ FEN ':
                    line_num += 1
                    continue
                else:
                    skip_blank = False

            if in_tag_section:
                if line == '':
                    movetext = []
                    in_tag_section = False
                else:
                    if len(line) > 0 and line[0] == ';':
                        # skip comment
                        line_num += 1
                        continue
                    m = tag_re.match(line)
                    if not m:
                        raise PgnError('missing tag section at line %d' % line_num)
                    tags[m.group(1)] = m.group(2).replace(r'\"', '"')
            else:
                if line == '':
                    # Search for the result to try to handle blank lines
                    # within the movetext.  This doesn't account for
                    # results within user comments, but works for now.
                    movetext_str = '\n'.join(movetext)
                    if not result_re.search(movetext_str):
                        movetext.append(line)
                        line_num += 1
                        continue
                    yield PgnGame(tags, movetext_str)
                    tags.clear()
                    skip_blank = True
                    in_tag_section = True
                else:
                    movetext.append(line)

            line_num += 1

        if len(tags) > 0:
            movetext_str = '\n'.join(movetext)
            yield PgnGame(tags, movetext_str)

        self.f.close()

class PgnGame(object):
    def __init__(self, tags, movetext):
        self.tags = copy.copy(tags)
        self.movetext = movetext
        self.is_checkmate = False
        self.is_stalemate = False
        self.is_repetition = False
        self.is_fifty = False
        #self.is_resign = False
        #self.partner_won = False
        self.initial_comments = []
        self.parse(movetext)
        assert('WhiteA' in self.tags)
        assert('BlackA' in self.tags)
        assert('WhiteB' in self.tags)
        assert('BlackB' in self.tags)

    def parse(self, s):
        """parses moves and their comments"""
        i = 0
        self.moves = []
        move_char = None
        while i < len(s):
            m = space_re.match(s, i)
            if m:
                i = m.end()
                continue

            m = result_re.match(s, i)
            if m:
                self.result = m.group(1)
                i = m.end()
                continue

            # The move_num re should come before the move re because
            # a move cannot start with a number.
            m = move_num_re.match(s, i)
            if m:
                move_char = m.group(2)
                i = m.end()
                continue

            m = dots_re.match(s, i)
            if m:
                i = m.end()
                continue

            m = move_re.match(s, i)
            if m:
                if m.group(2) is not None:
                    if '#' in m.group(2):
                        self.is_checkmate = True
                self.moves.append(BpgnMove(m.group(1), m.group(2), move_char))
                i = m.end()
                continue

            m = comment_re.match(s, i)
            if m:
                i = m.end()
                if checkmate_re.search(m.group(1)):
                    self.is_checkmate = True
                    m2 = checkmate_re.search(m.group(1))
                    who = m2.group(1)
                    if who == self.tags['WhiteA']:
                        self.mated = 'A'
                    elif who == self.tags['BlackA']:
                        self.mated = 'a'
                    elif who == self.tags['WhiteB']:
                        self.mated = 'B'
                    elif who == self.tags['BlackB']:
                        self.mated = 'b'
                    else:
                        raise PgnError('unknown player checkmated: %s' % who)
                elif stalemate_re.search(m.group(1)):
                    self.is_stalemate = True
                elif repetition_re.search(m.group(1)):
                    self.is_repetition = True
                elif fifty_re.search(m.group(1)):
                    self.is_fifty = True
                '''elif resign_re.search(m.group(1)):
                    self.is_resign = True
                    m2 = resign_re.search(m.group(1))
                    who = m2.group(1)
                    if who == self.tags['WhiteA']:
                        self.resigned = 'A'
                    elif who == self.tags['BlackA']:
                        self.resigned = 'a'
                    elif who == self.tags['WhiteB']:
                        self.resigned = 'B'
                    elif who == self.tags['BlackB']:
                        self.resigned = 'b'
                    else:
                        raise PgnError('unknown player resigned: %s' % who)
                elif partner_won_re.search(m.group(1)):
                    self.partner_won = True
                    m2 = partner_won_re.search(m.group(1))
                    who = m2.group(1)
                    if who == self.tags['WhiteA']:
                        self.won = 'b'
                    elif who == self.tags['BlackA']:
                        self.won = 'B'
                    elif who == self.tags['WhiteB']:
                        self.won = 'a'
                    elif who == self.tags['BlackB']:
                        self.won = 'A'
                    else:
                        raise PgnError("unknown player's partner won: %s" % who)'''
                if len(self.moves) > 0:
                    self.moves[-1].add_comment(m.group(1))
                else:
                    self.initial_comments.append(m.group(1))
                continue

            m = nag_re.match(s, i)
            if m:
                i = m.end()
                continue

            raise PgnError('unrecognized sytax in pgn: "%s"' % s[i:i+15])

    def __str__(self):
        return '%s vs. %s and %s vs. %s' % (self.tags['WhiteA'],
            self.tags['BlackA'], self.tags['WhiteB'], self.tags['BlackB'])

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
