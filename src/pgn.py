import re
import string
import copy

tag_re = re.compile(r'''\[(\w+)\s+"([^\n]*?)"\]\s*$''')
space_re = re.compile(r'''\s+''')
move_num_re = re.compile(r'''(\d+)\.*''')
move_re = re.compile(r'''([NBRQK]?[a-h1-8x]{2,5}(?:=[NBRQK])?|O-O-O|O-O)([+#])?''')
dots_re = re.compile(r'''\.\.\.''')
comment_re = re.compile(r'''\{(.*?)\}''', re.S)
nag_re = re.compile(r'''\$(\d+)''')
result_re = re.compile(r'''(1-0|0-1|1/2-1/2|\*)''')
checkmate_re = re.compile(r''' checkmated\s*$''')
stalemate_re = re.compile(r''' drawn by stalemate\s*$''')

class PgnError(Exception):
    def __init__(self, reason):
        self.reason = reason
        print reason

class PgnMove(object):
    def __init__(self, text, decorator):
        self.text = text
        self.decorator = decorator if decorator != None else ''
        self.comments = []

    def add_comment(self, com):
        self.comments.append(com)

class Pgn(object):
    def __init__(self, s):
        in_tag_section = True
        tags = {}
        self.games = []
        line_num = 0
        i = 0
        skip_blank = True
        lines = s.splitlines()
   
        while line_num < len(lines):
            line = lines[line_num]

            if skip_blank:
                if line == '':
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
                    movetext = string.joinfields(movetext, '\n')
                    self.games.append(PgnGame(tags, movetext))
                    tags.clear()
                    skip_blank = True
                    in_tag_section = True
                else:
                    movetext.append(line)

            line_num += 1

class PgnGame(object):
    def __init__(self, tags, movetext):
        self.tags = copy.copy(tags)
        self.movetext = movetext
        self.is_checkmate = False
        self.is_stalemate = False
        self.initial_comments = []
        self.parse(movetext)
        assert('White' in self.tags)

    def parse(self, s):
        """parses moves and their comments"""
        i = 0
        self.moves = []
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
                i = m.end()
                continue
            
            m = dots_re.match(s, i)
            if m:
                i = m.end()
                continue

            m = move_re.match(s, i)
            if m:
                if m.group(2) != None:
                    if '#' in m.group(2):
                        self.is_checkmate = True
                self.moves.append(PgnMove(m.group(1), m.group(2)))
                i = m.end()
                continue

            m = comment_re.match(s, i)
            if m:
                i = m.end()
                if checkmate_re.search(m.group(1)):
                    self.is_checkmate = True
                elif stalemate_re.search(m.group(1)):
                    self.is_stalemate = True
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
        return '%s vs. %s' % (self.tags['White'], self.tags['Black'])

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
