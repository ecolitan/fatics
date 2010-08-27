import copy

class GameList(object):
    def __init__(self):
        self.games = {}

    def primary(self):
        return self.games.values()[0]

    def add(self, game, opp_name):
        assert(opp_name not in self.games)
        self.games[opp_name] = game

    def free(self, opp_name):
        del self.games[opp_name]

    def __len__(self):
        return len(self.games)

    def iter(self):
        return self.games.itervalues()

    def leave_all(self, user):
        # python docs: "Using iteritems() while adding or deleting entries
        # in the dictionary may raise a RuntimeError or fail to iterate
        # over all entries."
        for (k, v) in copy.copy(self.games).iteritems():
            v.leave(user)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
