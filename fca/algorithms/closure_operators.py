# -*- coding: utf-8 -*-
"""Derivation and closure operators"""

from collections import defaultdict
import copy
from functools import reduce

def oprime(objects, context):
    """
    Compute the set of all attributes shared by objects in context.
    NB: objects must be of type set
    """
    attributes = set(context.attributes[:])
    for o in objects:
        attributes &= context.get_object_intent(o)
    return attributes

def aprime(attributes, context):
    """
    Compute the set of all objects sharing attributes in context.
    NB: attributes must be of type set
    """
    objects = set(context.objects[:])
    for a in attributes:
        objects &= context.get_attribute_extent(a)
    return objects
    
def oclosure(objects, context):
    """Return the closure of objects in context as a sorted list"""
    return sorted(aprime(oprime(objects, context), context))
    

def aclosure(attributes, context):
    """Return the closure of attributes in context as a sorted list"""
    return sorted(oprime(aprime(attributes, context), context))
    
    
def simple_closure(s, implications):
    """
    Input:  A collection of implications and an attribute set s
    Output: The closure of s with respect to implications
    
    @note: refactored by Artem Revenko to increase performance.
    
    Examples
    ========
    
    >>> from fca.implication import Implication
    >>> cd2a = Implication(set(('c', 'd')), set(('a')))
    >>> ad2c = Implication(set(('a', 'd')), set(('c')))
    >>> ab2cd = Implication(set(('a', 'b')), set(('c', 'd')))
    >>> imps = [cd2a, ad2c, ab2cd]
    >>> print simple_closure(set('a'), imps)
    set(['a'])
    >>> print simple_closure(set(), imps)
    set([])
    >>> simple_closure(set(['b', 'c', 'd']), imps) == set(['a', 'b', 'c', 'd'])
    True
    
    >>> a2bc = Implication(set(('a')), set(('b', 'c')))
    >>> ce2abd = Implication(set(('c', 'e')), set(('a', 'b', 'd')))
    >>> de2abc = Implication(set(('d', 'e')), set(('a', 'b', 'c')))
    >>> cd2abe = Implication(set(('c', 'd')), set(('a', 'b', 'e')))
    >>> imps = [a2bc, ce2abd, de2abc, cd2abe]
    >>> simple_closure(set(['b', 'a']), imps) == set(['a', 'b', 'c'])
    True
    >>> simple_closure(set(['a', 'e']), imps) == set(['a', 'b', 'c', 'd', 'e'])
    True
    >>> imps = [ce2abd, a2bc, de2abc, cd2abe]
    >>> simple_closure(set(['a', 'e']), imps) == set(['a', 'b', 'c', 'd', 'e'])
    True
    
    """
    unused_imps = implications[:]
    new_closure = s.copy()
    changed = True
    while changed:
        to_remove = set()
        changed = False
        for imp in unused_imps:
            if imp._premise <= new_closure:
                new_closure |= imp._conclusion
                changed = True
                to_remove.add(imp)
        unused_imps = [imp for imp in unused_imps if not imp in to_remove]
    return new_closure
    
def lin_closure(s, implications):
    """
    Input:  A collection of implications and an attribute set s
    Output: The closure of s with respect to implications
    NB: This implementation is not linear-time.
        Use lists instead of dicts to get a liner-time implementation.
        
    @note: refactored by Artem Revenko to increase performance.
    
    Examples
    ========
    
    >>> from fca.implication import Implication
    >>> cd2a = Implication(set(('c', 'd')), set(('a')))
    >>> ad2c = Implication(set(('a', 'd')), set(('c')))
    >>> ab2cd = Implication(set(('a', 'b')), set(('c', 'd')))
    >>> imps = [cd2a, ad2c, ab2cd]
    >>> print lin_closure(set('a'), imps)
    set(['a'])
    >>> print lin_closure(set(), imps)
    set([])
    >>> lin_closure(set(['b', 'c', 'd']), imps) == set(['a', 'b', 'c', 'd'])
    True
    
    >>> a2bc = Implication(set(('a')), set(('b', 'c')))
    >>> ce2abd = Implication(set(('c', 'e')), set(('a', 'b', 'd')))
    >>> de2abc = Implication(set(('d', 'e')), set(('a', 'b', 'c')))
    >>> cd2abe = Implication(set(('c', 'd')), set(('a', 'b', 'e')))
    >>> imps = [a2bc, ce2abd, de2abc, cd2abe]
    >>> lin_closure(set(['b', 'a']), imps) == set(['a', 'b', 'c'])
    True
    >>> lin_closure(set(['a', 'e']), imps) == set(['a', 'b', 'c', 'd', 'e'])
    True
    >>> imps = [ce2abd, a2bc, de2abc, cd2abe]
    >>> lin_closure(set(['a', 'e']), imps) == set(['a', 'b', 'c', 'd', 'e'])
    True
    
    """
    def decrease_count(i):
        imp = current_imps[i]
        if count[imp] == 0:
            return set()
        count[imp] -= 1
        if count[imp] == 0:
            return imp._conclusion
        return set()
    
    if not implications:
        return s
    new_closure = s.copy()
    new_closure = reduce(set.union,
                         [imp._conclusion for imp in implications if not imp.premise],
                         new_closure)
    count_ls = [(imp, len(imp.premise)) for imp in implications]
    count = dict(count_ls)
    imps_ls = [(attr, imp) for imp in implications for attr in imp.premise]
    imps = defaultdict(list)
    for n,v in imps_ls:
        imps[n].append(v)
    update = list(new_closure)
    
    while update:
        m = update.pop()
        current_imps = imps[m]
        add = reduce(set.union,
                     list(map(decrease_count, list(range(len(current_imps))))),
                     set()) - new_closure
        new_closure |= add
        update.extend(add)
        
    return new_closure


def closure(current, base_set, implications, prefLen):
    """
    return the closure of attributes
    NB: current and base_set must be of type set
    """
    unused_imps = copy.copy(implications)
    old_closure = copy.copy(base_set)
    new_closure = copy.copy(current)
    
    while (old_closure != new_closure):
        old_closure = copy.copy(new_closure)
        delete_list = []
        
        for imp in unused_imps:
            if imp.get_premise() <= new_closure:
                new_closure |= imp.get_conclusion()
                
                for x in base_set[:prefLen]:
                    if (((x in new_closure) and not (x in current)) 
                        or (not (x in new_closure) and (x in current))):
                        return False, set()
                
                delete_list.append(imp)
                
        for imp in delete_list:
            unused_imps.remove(imp)
    
    return True, new_closure    
                

if __name__ == "__main__":
    import doctest
    doctest.testmod()