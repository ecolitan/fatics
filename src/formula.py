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

"""
This design follows "Simple Top-Down Pasing in Python" by Fredrik Lundh,
whish uses an algorithm originally published by Vaughan Pratt.
http://effbot.org/zone/simple-top-down-parsing.htm

Terminology:
    nud = null denotation
    led = left denotation
    lbp = left binding power

Kudos to Dave Herscovici for the excellent original FICS implementation
of formulas, which I tried to emulate.
"""
import re

all_tokens = {}

class FormulaError(Exception):
    def __init__(self, msg):
        super(FormulaError, self).__init__()
        self.msg = msg

class Symbol(object):
    tokens = []
    def nud(self):
        raise FormulaError('unexpected use as unary operator')

    def led(self, left):
        raise FormulaError('unexpected use as binary operator')

class Token(object):
    """ decorator that registers tokens for the tokenizer """
    def __init__(self, tokens):
        self.tokens = tokens
    def __call__(self, cls):
        for tok in self.tokens:
            all_tokens[tok] = cls
        cls.tokens = self.tokens
        def new_cls(*args):
            cls(*args)
        return new_cls

class NumSymbol(Symbol):
    def __init__(self, val):
        self.val = val
    def nud(self):
        return self.val

def advance(sym):
    global token
    if sym not in token.tokens:
        raise FormulaError('expected %s' % sym)
    token = nextt()

@Token(['!'])
class NotSymbol(Symbol):
    lbp = 90
    def nud(self):
        return not expression(90)

@Token(['*'])
class MultSymbol(Symbol):
    lbp = 80
    def led(self, left):
        right = expression(80)
        return left * right

@Token(['/'])
class DivSymbol(Symbol):
    lbp = 80
    def led(self, left):
        right = expression(80)
        if right == 0:
            right = .001 # fudge factor
        return left // right

@Token(['+'])
class AddSymbol(Symbol):
    lbp = 70
    def nud(self):
        # unary + has higher precedence
        return expression(90)
    def led(self, left):
        right = expression(70)
        return left + right

@Token(['-'])
class SubSymbol(Symbol):
    lbp = 70
    def nud(self):
        # unary - has higher precedence
        return -expression(90)
    def led(self, left):
        right = expression(70)
        return left - right

@Token(['<'])
class LTSymbol(Symbol):
    lbp = 60
    def led(self, left):
        right = expression(60)
        return left < right

@Token(['<=', '=<'])
class LTESymbol(Symbol):
    lbp = 60
    def led(self, left):
        right = expression(60)
        return left <= right

@Token(['>'])
class GTSymbol(Symbol):
    lbp = 60
    def led(self, left):
        right = expression(60)
        return left > right

@Token(['>=', '=>'])
class GTESymbol(Symbol):
    lbp = 60
    def led(self, left):
        right = expression(60)
        return left >= right

@Token(['=', '=='])
class EqSymbol(Symbol):
    lbp = 50
    def led(self, left):
        right = expression(50)
        return left == right

@Token(['!=', '<>'])
class NeqSymbol(Symbol):
    lbp = 40
    def led(self, left):
        right = expression(40)
        return left != right

@Token(['&', '&&', 'and'])
class AndSymbol(Symbol):
    lbp = 30
    def led(self, left):
        right = expression(30)
        return left and right

@Token(['|', '||', 'or'])
class OrSymbol(Symbol):
    lbp = 20
    def led(self, left):
        right = expression(20)
        return left or right

@Token(['('])
class LParenSymbol(Symbol):
    lbp = 0
    def nud(self):
        expr = expression(0)
        advance(')')
        return expr

@Token([')'])
class RParenSymbol(Symbol):
    lbp = 0

class EndSymbol(Symbol):
    lbp = 0

@Token(['abuser'])
class AbuserSymbol(Symbol):
    lbp = 0
    def nud(self):
        return chal.a.has_title('abuser') if chal else None

@Token(['computer'])
class ComputerSymbol(Symbol):
    lbp = 0
    def nud(self):
        return chal.a.has_title('computer') if chal else None

@Token(['time'])
class TimeSymbol(Symbol):
    lbp = 0
    def nud(self):
        return chal.time if chal else None

@Token(['inc'])
class IncSymbol(Symbol):
    lbp = 0
    def nud(self):
        return chal.inc if chal else None

@Token(['rating'])
class RatingSymbol(Symbol):
    lbp = 0
    def nud(self):
        return int(chal.a.get_rating(chal.speed_variant)) if chal else None

@Token(['myrating'])
class MyratingSymbol(Symbol):
    lbp = 0
    def nud(self):
        return int(chal.b.get_rating(chal.speed_variant)) if chal else None

@Token(['ratingdiff'])
class RatingdiffSymbol(Symbol):
    lbp = 0
    def nud(self):
        return (int(chal.a.get_rating(chal.speed_variant)) -
            int(chal.b.get_rating(chal.speed_variant))) if chal else None

@Token(['white'])
class WhiteSymbol(Symbol):
    lbp = 0
    def nud(self):
        return chal.side == WHITE if chal else None

@Token(['black'])
class BlackSymbol(Symbol):
    lbp = 0
    def nud(self):
        return chal.side == BLACK if chal else None

@Token(['nocolor'])
class NocolorSymbol(Symbol):
    lbp = 0
    def nud(self):
        return (chal.side not in [WHITE, BLACK]) if chal else None

@Token(['slow'])
class StandardSymbol(Symbol):
    lbp = 0
    def nud(self):
        return chal.speed_name == 'slow' if chal else None

@Token(['standard'])
class StandardSymbol(Symbol):
    lbp = 0
    def nud(self):
        return chal.speed_name == 'standard' if chal else None

@Token(['blitz'])
class BlitzSymbol(Symbol):
    lbp = 0
    def nud(self):
        return chal.speed_name == 'blitz' if chal else None

@Token(['lightning'])
class LightningSymbol(Symbol):
    lbp = 0
    def nud(self):
        return chal.speed_name == 'lightning' if chal else None

@Token(['registered'])
class RegisteredSymbol(Symbol):
    lbp = 0
    def nud(self):
        return (0 if chal.a.is_guest else 1) if chal else None

@Token(['timeseal'])
class TimesealSymbol(Symbol):
    lbp = 0
    def nud(self):
        return chal.a.has_timeseal() if chal else None

@Token(['crazyhouse'])
class CrazyhouseSymbol(Symbol):
    lbp = 0
    def nud(self):
        return chal.variant.name == 'crazyhouse' if chal else None

class FSymbol(Symbol):
    lbp = 0
    def __init__(self, num):
        self.num = num
    def nud(self):
        global token, nextt, chal, f_num
        if self.num <= f_num:
            raise FormulaError('A formula variable may not refer to itself or an earlier formula variable')
        if not chal:
            # no need to evaluate
            return None
        old_token = token
        old_nextt = nextt
        ret = check_formula(chal, chal.b.vars['f' + str(self.num)], self.num)
        token = old_token
        nextt = old_nextt
        return ret

def expression(rbp = 0):
    global token, nextt
    t = token
    try:
        token = nextt()
    except StopIteration:
        # consider an empty formula to be 1
        if rbp == 0:
            return 1
        else:
            raise FormulaError('unexpected end of formula')
    left = t.nud()
    while rbp < token.lbp:
        t = token
        token = nextt()
        left = t.led(left)
    return left

escaped_re = re.compile(r'([*+()|])')
def re_escape(s):
    return escaped_re.sub(r'\\\1', s)

digit_re = re.compile(r'^(\d+)(.*)')
fvar_re = re.compile(r'^f([1-9])(.*)')
minute_re = re.compile(r'^\s*minutes?(.*)')
tokenize_re = re.compile('^(' + '|'.join([re_escape(k) for k in sorted(list(all_tokens.keys()), key=len, reverse=True)]) + ')(.*)')
comment_re = re.compile('#.*')
def tokenize(s):
    s = comment_re.sub('', s)
    while True:
        s = s.lstrip()
        if len(s) == 0:
            break
        m = digit_re.match(s)
        if m:
            val = int(m.group(1))
            s = m.group(2)
            m = minute_re.match(s)
            if m:
                val *= 60
                s = m.group(1)
            yield NumSymbol(val)
            continue

        m = fvar_re.match(s)
        if m:
            num = int(m.group(1))
            s = m.group(2)
            yield FSymbol(num)
            continue

        m = tokenize_re.match(s)
        if m:
            s = m.group(2)
            yield all_tokens[m.group(1)]()
            continue

        raise FormulaError('Error parsing formula')
    yield EndSymbol()

def check_formula(chal_, s, num=0):
    """ Check whether the challenge CHAL_ meets the formula described by S.
    If chal_ is None, we parse the formula for validity but don't worry
    about its evaulation.

    NUM is 0 for the main formula var, 1 for f1, 2 for f2, etc.

    Raises FormulaError on an error.
    """
    if s is None:
        # no formula
        return 1
    assert(type(s) == str)
    global token, nextt, chal, f_num
    chal = chal_
    try:
        nextt = tokenize(s).next
    except StopIteration:
        raise FormulaError('got formula with no tokens')
    f_num = num
    token = nextt()
    return expression()

if __name__ == '__main__':
    print(check_formula(None, '7 * (3 * (3 + 2) /  2) - 42 * 2'))
    print(check_formula(None, '(2 + 5 * 5) - 1'))
    print(check_formula(None, '(2 + 5 * 5) - 1'))
    print(check_formula(None, '!lightning && !blitz'))
    print(check_formula(None, '1000 <= 1500 and 1500 <= 2000'))
    try:
        print(check_formula(None, '33-'))
    except FormulaError:
        print('success')
    else:
        print 'FAIL'

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
