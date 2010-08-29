import re
import copy

tag_re = re.compile(r'''\[(\w+)\s+"([^\n]*?)"\]\s*$''')
space_re = re.compile(r'''\s+''')
move_num_re = re.compile(r'''(\d+)\.*''')
move_re = re.compile(r'''([NBRQK]?[a-h1-8x]{2,5}(?:=[NBRQK])?|[PNBRQpnbrq]@[a-h][1-8]|O-O-O|O-O)([+#])?''')
dots_re = re.compile(r'''\.\.\.''')
comment_re = re.compile(r'''\{(.*?)\}''', re.S)
nag_re = re.compile(r'''\$(\d+)''')
result_re = re.compile(r'''(1-0|0-1|1/2-1/2|\*)''')
checkmate_re = re.compile(r'''\s+checkmated\s*$''')
stalemate_re = re.compile(r'''\s+drawn\s+by\s+stalemate\s*$''')
repetition_re = re.compile(r'''\s+drawn\s+by\s+repetition\s*$''')
fifty_re = re.compile(r'''\s+drawn\s+by\s+the\s+50\s+move\s+rule\s*$''')
nomaterial_re = re.compile(r'''[nN]either\s+player\s+has\s+mating\s+material\s*$''')

class PgnError(Exception):
    def __init__(self, reason):
        self.reason = reason
        print reason

class PgnMove(object):
    def __init__(self, text, decorator):
        self.text = text
        self.decorator = decorator if decorator is not None else ''
        self.comments = []

    def add_comment(self, com):
        self.comments.append(com)

class Pgn(object):
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
        self.is_draw_nomaterial = False
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
                if m.group(2) is not None:
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
                elif repetition_re.search(m.group(1)):
                    self.is_repetition = True
                elif fifty_re.search(m.group(1)):
                    self.is_fifty = True
                elif nomaterial_re.search(m.group(1)):
                    self.is_draw_nomaterial = True

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
