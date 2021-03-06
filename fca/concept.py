# -*- coding: utf-8 -*-
"""
Contains base class for formal concept
"""
import itertools


class Concept(object):
    """ 
    A formal concept, contains intent and extent 
    
    Examples
    ========

    Create a concept with extent=['Earth', 'Mars', 'Mercury', 'Venus']
    and intent=['Small size', 'Near to the sun'].
    
    >>> extent = ['Earth', 'Mars', 'Mercury', 'Venus']
    >>> intent = ['Small size', 'Near to the sun']
    >>> c = Concept(extent, intent)
    >>> 'Earth' in c.extent
    True
    >>> 'Pluto' in c.extent
    False
    >>> 'Small size' in c.intent
    True

    Print a concept.

    >>> print c
    (['Earth', 'Mars', 'Mercury', 'Venus'], ['Near to the sun', 'Small size'])

    """
    # TODO: add __eq__
    
    def __init__(self, extent, intent):
        """Initialize a concept with given extent and intent """
        self.extent = set(extent)
        self.intent = set(intent)
        self.meta = {}

    def __str__(self):
        """Return a string representation of a concept"""
        if len(self.intent) > 0:
            e = list(self.extent)
            e.sort()
        else:
            # TODO: Sometimes |intent| > 0, but extent is G.
            e = "G"
        if len(self.extent) > 0:
            i = list(self.intent)
            i.sort()
        else:
            # TODO: Sometimes |extent| > 0, but intent is M.
            i = "M"
        if len(list(self.meta.keys())) != 0:
            s = " meta: {0}".format(self.meta)
        else:
            s = ""
        return "({0}, {1}){2}".format(e, i, s)
    
    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return (type(self) == type(other) and
                self.extent == other.extent and
                self.intent == other.intent)

    def __hash__(self):
        return hash(str(self))

    def pairs(self):
        if not self.extent or not self.intent:
            return []
        else:
            out = itertools.product(self.extent, self.intent)
            return out

if __name__ == "__main__":
    import doctest
    doctest.testmod()
