# -*- coding: utf-8 -*-
"""
Contains class for implications
"""

class Implication(object):
    """
    An Implication consists of two sets: *premise* and *conclusion*
    
    Examples
    ========
    
    >>> imp = Implication({'a', 'b'}, {'c'})
    >>> imp
    a, b => c
    >>> print imp
    a, b => c
    >>> imp.is_respected({'a', 'b'})
    False
    >>> imp.is_respected({'a', 'b', 'c'})
    True
    >>> imp.is_respected({'a', 'c'})
    True
    >>> imp.is_respected({'b'})
    True
    """

    def __init__(self, premise = set(), conclusion = set()):
        """
        Create implication from two sets of attributes
        """
        self._premise = set(premise)
        self._conclusion = set(conclusion)
        
    def __deepcopy__(self, memo):
        return Implication(self._premise.copy(), self._conclusion.copy())

    def get_premise(self):
        """
        Return premise of implication
        """
        return self._premise
        
    def get_conclusion(self):
        """
        Return conclusion of implication
        """
        return self._conclusion

    def get_reduced_conclusion(self):
        return self._conclusion - self._premise
    
    premise = property(get_premise)
    conclusion = property(get_reduced_conclusion)
        
    def __repr__(self):
        try:
            premise = ", ".join([element for element in self._premise])
            short_conclusion = self._conclusion - self._premise
            conclusion = ", ".join([element for element in short_conclusion])
        except:
            premise = ", ".join([str(element) for element in self._premise])
            short_conclusion = self._conclusion - self._premise
            conclusion = ", ".join([str(element) for element in short_conclusion])
        return " => ".join((premise, conclusion,))
        
    def __unicode__(self):
        return self.__repr__()

    def __eq__(self, other):
        if ((self.premise == other.premise) and
                (self.conclusion == other.conclusion)):
            return 1
        else:
            return 0

    def __hash__(self):
        return hash(str(self))
            
    def is_respected(self, some_set):
        """Checks whether *some_set* respects an implication or not"""
        # if some_set contains every element from premise and not every
        # element from conclusion then it doesn't respect an implication
        if type(some_set) == set:
            return not self.premise <= some_set or self.conclusion <= some_set
        else:
            # Assume a partial example
            return (self.conclusion <= some_set[1] or
                    not self.premise <= some_set[0])
            
    @classmethod
    def str2imp(cls, string):
        def str2set(str_):
            return set(map(str.strip, str_.split(',')))
        str_premise, str_conclusion = string.split('=>')
        premise = str2set(str_premise)
        conclusion = str2set(str_conclusion)
        return cls(premise, conclusion)

        
class UnitImplication(Implication):
    def __init__(self, premise = set(), conclusion = None):
        """
        Create implication from set *premise* and element *conclusion*
        """
        # if isinstance(conclusion, set):
        #     conclusion = frozenset(conclusion)
        set_conclusion = {conclusion}
        super().__init__(premise, set_conclusion)

    def get_reduced_conclusion(self):
        conclusion = super().conclusion
        assert len(conclusion) == 1
        return conclusion
    
    conclusion = property(get_reduced_conclusion)


class NegativeImplication(Implication):
    def __repr__(self):
        try:
            premise = ", ".join([element for element in self.premise])
            conclusion = ("not (" +
                          ", ".join([element for element in self.conclusion]) +
                          ")")
        except:
            premise = ", ".join([str(element) for element in self.premise])
            conclusion = ("not (" +
                          ", ".join([str(element)
                                     for element in self.conclusion]) +
                          ")")
        return " => ".join((premise, conclusion,))


    def is_respected(self, some_set):
        """Checks whether *some_set* respects the negative implication"""
        # if some_set contains every element from premise and any
        # element from conclusion then it doesn't respect an implication
        if type(some_set) == set:
            return (not self.premise <= some_set or
                    not (self.conclusion & some_set))
        else:
            # Assume a partial example
            return (not (self.conclusion & some_set[1]) or
                    not self.premise <= some_set[0])
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()