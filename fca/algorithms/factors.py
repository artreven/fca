"""
Holds functions for finding optimal factors for decomposition of context.

Created on Jan 8, 2014

@author: artreven
"""
import itertools
import collections

import fca
from . import closure_operators as co

def make_factor_cxts(factors=[]):
    """
    Make two contexts: objects-factors and factors-attributes out of tuple of
    given concepts.
    
    @param factors: tuple of *fca.Concept*s (or anything that has *extent* and 
    *intent* instance variables).
    """
    def el_ind(el, el_dict):
        try:
            return el_dict[el]
        except KeyError:
            num_els = len(el_dict)
            el_dict[el] = num_els
            return num_els
    objs_dict = dict()
    atts_dict = dict()
    table_objs_fcts = []
    table_fcts_atts = []
    for c in factors:
        table_objs_fcts.append(set(el_ind(obj, objs_dict) for obj in c.extent))
        table_fcts_atts.append(set(el_ind(att, atts_dict) for att in c.intent))
    # sort objs and atts in order of appearance to get correct factor ex/intents
    attributes = sorted(list(atts_dict.keys()), key=atts_dict.__getitem__)
    objects = sorted(list(objs_dict.keys()), key=objs_dict.__getitem__)
    num_atts = len(attributes)
    num_objs = len(objects)
    names_fcts = ['f{}'.format(x) for x in range(len(factors))]
    table_objs_fcts = list(zip(*[[(x in row) for x in range(num_objs)]
                            for row in table_objs_fcts]))
    table_fcts_atts = [[(x in row) for x in range(num_atts)]
                       for row in table_fcts_atts]
    return (fca.Context(table_objs_fcts, objects, names_fcts),
            fca.Context(table_fcts_atts, names_fcts, attributes))


def _oplus(D, y, cxt, U):
    Dplusy = D | {y}
    pr = set(itertools.product(co.aprime(Dplusy, cxt),
                               co.aclosure(Dplusy, cxt)))
    result = pr & U
    return result


def algorithm2(cxt):
    """
    Algorithm2 from article{
    title = "Discovery of optimal factors in binary data via a novel method of matrix decomposition ",
    journal = "Journal of Computer and System Sciences ",
    volume = "76",
    number = "1",
    pages = "3 - 20",
    year = "2010",
    doi = "http://dx.doi.org/10.1016/j.jcss.2009.05.002",
    url = "http://www.sciencedirect.com/science/article/pii/S0022000009000415",
    author = "Radim Belohlavek and Vilem Vychodil"}
    """
    U = set(cxt.object_attribute_pairs)
    F = []
    while U:
        D = set()
        V = 0
        to_remove = set()
        while True:
            ls_measures = [(len(_oplus(D, j, cxt, U)), j)
                           for j in set(cxt.attributes) - D]
            if ls_measures:
                maxDj = max(ls_measures, key=lambda x: x[0])
            else:
                maxDj = [0,]
            if maxDj[0] > V:
                j = maxDj[1]
                D = set(co.aclosure(D | {j}, cxt))
                C = set(co.aprime(D, cxt))
                to_remove = set(itertools.product(C, D)) & U
                V = len(to_remove)
            else:
                break
        F.append(fca.Concept(C, D))
        U -= to_remove
        if len(to_remove) == 0:
            print('Algorithm stuck, something went wrong, pairs left ', len(U))
            assert False
    return F
