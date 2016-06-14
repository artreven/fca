# -*- coding: utf-8 -*-
"""Holds implementation of Norris' algorithm"""

from copy import copy
from fca import Concept, ConceptSystem


def norris(context, with_parents=True):
    """Build all concepts of a context
    
    Based on the Norris' algorithm for computing the maximal rectangles
    in a binary relation.

    Returns the ConceptSystem instance with a full set of concepts

    Examples
    ========

    >>> from fca import Context, ConceptLattice
    >>> ct = [[True, False, False, True],\
              [True, False, True, False],\
              [False, True, True, False],\
              [False, True, True, True]]
    >>> objs = [1, 2, 3, 4]
    >>> attrs = ['a', 'b', 'c', 'd']
    >>> c = Context(ct, objs, attrs)
    >>> cl = ConceptLattice(c, builder=norris)
    >>> print cl
    ([], M)
    ([1], ['a', 'd'])
    ([2], ['a', 'c'])
    ([1, 2], ['a'])
    ([3, 4], ['b', 'c'])
    ([2, 3, 4], ['c'])
    (G, [])
    ([4], ['b', 'c', 'd'])
    ([1, 4], ['d'])

    """
    # To be more efficient we store intent (as Python set) of every 
    # object to the list
    # TODO: Move to Context class?
    examples = []
    for ex in context.examples():
        examples.append(ex)
    
    cs = [Concept([], context.attributes)]
    for i in range(len(context)):
        cs_for_loop = cs[:]
        for c in cs_for_loop:
            if c.intent.issubset(examples[i]):
                c.extent.add(context.objects[i])
            else:
                new_intent = c.intent & examples[i]
                new = True
                for j in range(i):
                    if new_intent.issubset(examples[j]) and\
                       context.objects[j] not in c.extent:
                        new = False
                        break
                if new:
                    cs.append(Concept({context.objects[i]} | c.extent,
                        new_intent))
    if with_parents:
        return (cs, compute_covering_relation(cs))
    else:
        return cs


def compute_covering_relation(cs):
    """Computes covering relation for a given concept system.

    Returns a dictionary containing sets of parents for each concept.

    Examples
    ========

    """
    parents = dict([(c, set()) for c in cs])

    for i in range(len(cs)):
        for j in range(len(cs)):
            if cs[i].intent < cs[j].intent:
                parents[cs[j]].add(cs[i])
                for k in range(len(cs)):
                    if cs[i].intent < cs[k].intent < cs[j].intent:
                        parents[cs[j]].remove(cs[i])
                        break
    return parents
