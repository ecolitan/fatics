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

# originally by David Hain <dhain at spideroak com>
# licensed under GPLv3
# modified by Wil Mahan <wmahan at gmail.com>: add a simpler interface
# that returns a list of child nodes when there is no matching node,
# and a method to get all children of a given key

class NeedMore(Exception):
    def __init__(self, matches=None):
        self.matches = matches

class Node(object):
    """Internal representation of Trie nodes."""
    __slots__ = 'parent key nodes value'.split()
    no_value = object()

    def __init__(self, parent, key, nodes, value):
        self.parent = parent
        self.key = key
        self.nodes = nodes
        self.value = value

    """@property
    def keypath(self):
        n = self
        keypath = [n.key for n in iter(lambda: n.parent, None) if n.key]
        keypath.reverse()
        keypath.append(self.key)
        return keypath"""

    def walk(self):
        nodes = [self]
        while nodes:
            node = nodes.pop()
            if node.value is not node.no_value:
                yield node
            nodes.extend(node.nodes[key] for key in sorted(node.nodes, reverse=True))


class Trie(object):
    """A simple prefix tree (trie) implementation.

    If attempting to access a node without a value, but with descendents,
    NeedMore will be raised. If there are no descendents, KeyError will be
    raised.

    Usage:

    >>> import trie
    >>> from pprint import pprint
    >>> t = trie.Trie()
    >>> t['foobaz'] = 'Here is a foobaz.'
    >>> t['foobar'] = 'This is a foobar.'
    >>> t['fooqat'] = "What's a fooqat?"
    >>> pprint(list(t))
    [['f', 'o', 'o', 'b', 'a', 'r'],
     ['f', 'o', 'o', 'b', 'a', 'z'],
     ['f', 'o', 'o', 'q', 'a', 't']]
    >>> pprint(list(t.iteritems()))
    [(['f', 'o', 'o', 'b', 'a', 'r'], 'This is a foobar.'),
     (['f', 'o', 'o', 'b', 'a', 'z'], 'Here is a foobaz.'),
     (['f', 'o', 'o', 'q', 'a', 't'], "What's a fooqat?")]
    >>> t['foo']
    Traceback (most recent call last):
        ...
    NeedMore
    >>> t['fooqux']
    Traceback (most recent call last):
        ...
    KeyError: 'fooqux'
    >>> t.children('fooba')
    {'r': 'This is a foobar.', 'z': 'Here is a foobaz.'}
    >>> del t['foobaz']
    >>> pprint(list(t.iteritems()))
    [(['f', 'o', 'o', 'b', 'a', 'r'], 'This is a foobar.'),
     (['f', 'o', 'o', 'q', 'a', 't'], "What's a fooqat?")]
    """

    def __init__(self, root_data=Node.no_value, mapping=()):
        """Initialize a Trie instance.

        Args (both optional):
            root_data:  value of the root node (ie. Trie('hello')[()] == 'hello').
            mapping:    a sequence of (key, value) pairs to initialize with.
        """
        self.root = Node(None, None, {}, root_data)
        self.extend(mapping)

    def extend(self, mapping):
        """Update the Trie with a sequence of (key, value) pairs."""
        for k, v in mapping:
            self[k] = v

    def __setitem__(self, k, v):
        n = self.root
        for c in k:
            n = n.nodes.setdefault(c, Node(n, c, {}, Node.no_value))
        n.value = v

    def _getnode(self, k):
        n = self.root
        for c in k:
            try:
                n = n.nodes[c]
            except KeyError:
                raise KeyError(k)
        return n

    def __getitem__(self, k):
        n = self._getnode(k)
        if n.value is Node.no_value:
            if n.nodes:
                raise NeedMore()
            else:
                raise KeyError(k)
        return n.value

    """like __getitem__, but returns the matches"""
    def get(self, k):
        n = self._getnode(k)
        if n.value is Node.no_value:
            if n.nodes:
                children = self.all_children(k)
                assert(len(children) > 0)
                if len(children) == 1:
                    ret = children[0]
                elif len(children) > 0:
                    raise NeedMore(children)
            else:
                raise KeyError(k)
        else:
            ret = n.value
        return ret

    def __delitem__(self, k):
        n = self._getnode(k)
        if n.value is Node.no_value:
            raise KeyError(k)
        n.value = Node.no_value
        while True:
            if n.nodes or not n.parent:
                break
            del n.parent.nodes[n.key]
            n = n.parent

    def children(self, k):
        """Return a dict of the immediate children of the given key.

        Example:
        >>> t = Trie()
        >>> t['foobaz'] = 'Here is a foobaz.'
        >>> t['foobar'] = 'This is a foobar.'
        >>> t.children('fooba')
        {'r': 'This is a foobar.', 'z': 'Here is a foobaz.'}
        """
        n = self._getnode(k)
        return dict((k, n.nodes[k].value)
                    for k in n.nodes
                    if n.nodes[k].value is not Node.no_value)

    def _all_children_help(self, n, ret):
        if n.value is not Node.no_value:
            ret.append(n.value)
        for k in n.nodes:
            self._all_children_help(n.nodes[k], ret)

    def all_children(self, k):
        """Return a list of all children of the given key."""
        n = self._getnode(k)
        ret = []
        self._all_children_help(n, ret)
        return ret

    '''def __iter__(self):
        """Yield the keys in order."""
        for node in self.root.walk():
            yield node.keypath

    def iteritems(self):
        """Yield (key, value) pairs in order."""
        for node in self.root.walk():
            yield node.keypath, node.value'''

    # XXX slow!
    def itervalues(self):
        """Yield values in order."""
        for node in self.root.walk():
            yield node.value

if __name__ == '__main__':
    import doctest
    doctest.testmod()

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
