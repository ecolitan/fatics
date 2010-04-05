"""
Copyright (c) 2009 Ryan Kirkman

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
"""

import math
import time
import datetime

import rating

scale = 400 / math.log(10)

class Player:
    # Class attribute
    # The system constant, which constrains
    # the change in volatility over time.
    _tau = 0.5

    def __init__(self, rating, rd, vol, ltime):
        """ Values are on a glicko 2 scale; use to_glicko() to convert
        to original glicko scale """
        self.rating = rating
        self.ltime = ltime
        self._rd = rd
        self.vol = vol

    def get_current_rd(self):
        """ Calculates the player's current rating deviation. """
        # number of 1-minute rating periods passed since the last rd update
        t = (time.mktime(datetime.datetime.utcnow().timetuple())
            - time.mktime(self.ltime.timetuple())) / 60.0
        ret = math.sqrt(math.pow(self._rd, 2) + t * math.pow(self.vol, 2))
        #print '%f minutes, vol %f = %f' % (t, self.vol, ret)
        ret = min(ret, 350.0 / scale)
        return ret

    def update_player(self, rating_list, RD_list, outcome_list):
        """ Calculates the new rating and rating deviation of the player.

        update_player(list[int], list[int], list[bool]) -> None

        """
        v = self._v(rating_list, RD_list)
        self.vol = self._newVol(rating_list, RD_list, outcome_list, v)

        self._rd = 1 / math.sqrt((1 / math.pow(self.get_current_rd(), 2)) +
            (1 / v))

        tempSum = 0
        for i in range(len(rating_list)):
            tempSum += self._g(RD_list[i]) * \
                       (outcome_list[i] - self._E(rating_list[i], RD_list[i]))
        self.rating += math.pow(self._rd, 2) * tempSum


    def _newVol(self, rating_list, RD_list, outcome_list, v):
        """ Calculating the new volatility as per the Glicko2 system.

        _newVol(list, list, list) -> float

        """
        i = 0
        delta = self._delta(rating_list, RD_list, outcome_list, v)
        a = math.log(math.pow(self.vol, 2))
        tau = self._tau
        x0 = a
        x1 = 0

        while x0 != x1:
            # New iteration, so x(i) becomes x(i-1)
            x0 = x1
            d = math.pow(self.rating, 2) + v + math.exp(x0)
            h1 = -(x0 - a) / math.pow(tau, 2) - 0.5 * math.exp(x0) \
            / d + 0.5 * math.exp(x0) * math.pow(delta / d, 2)
            h2 = -1 / math.pow(tau, 2) - 0.5 * math.exp(x0) * \
            (math.pow(self.rating, 2) + v) \
            / math.pow(d, 2) + 0.5 * math.pow(delta, 2) * math.exp(x0) \
            * (math.pow(self.rating, 2) + v - math.exp(x0)) / math.pow(d, 3)
            x1 = x0 - (h1 / h2)

        return math.exp(x1 / 2)

    def _delta(self, rating_list, RD_list, outcome_list, v):
        """ The delta function of the Glicko2 system.

        _delta(list, list, list) -> float

        """
        tempSum = 0
        for i in range(len(rating_list)):
            tempSum += self._g(RD_list[i]) * (outcome_list[i] - self._E(rating_list[i], RD_list[i]))
        return v * tempSum

    def _v(self, rating_list, RD_list):
        """ The v function of the Glicko2 system.

        _v(list[int], list[int]) -> float

        """
        tempSum = 0
        for i in range(len(rating_list)):
            tempE = self._E(rating_list[i], RD_list[i])
            tempSum += math.pow(self._g(RD_list[i]), 2) * tempE * (1 - tempE)
        return 1 / tempSum

    def _E(self, p2rating, p2RD):
        """ The Glicko E function.

        _E(int) -> float

        """
        return 1 / (1 + math.exp(-1 * self._g(p2RD) * \
                                 (self.rating - p2rating)))

    def _g(self, RD):
        """ The Glicko2 g(RD) function.

        _g() -> float

        """
        return 1 / math.sqrt(1 + 3 * math.pow(RD, 2) / math.pow(math.pi, 2))


    def get_glicko(self):
        return rating.Rating(self.rating * scale + 1500,
            self.get_current_rd() * scale, self.vol,
            datetime.datetime.utcnow())

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
