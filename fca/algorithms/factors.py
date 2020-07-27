"""
Holds functions for finding optimal factors for decomposition of context.

Created on Jan 8, 2014

@author: artreven
"""
import itertools
import collections
import random
from typing import Tuple, Set

import fca


def make_factor_cxts(factors=None):
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

    if factors is None:
        factors = []
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


def _oplus(D_objs: Set[str], y: str,
           cxt: 'fca.Context',
           U: Set[Tuple[str, str]]):
    yprime = cxt.get_attribute_extent(y)
    Dy_prime = D_objs & yprime
    Dy_primeprime = cxt.oprime(Dy_prime)
    cpt = fca.Concept(extent=Dy_prime, intent=Dy_primeprime)
    # result = {x for x in cpt.pairs() if x not in U}
    result = set(cpt.pairs()) & U
    return result


def algorithm2(cxt, fidelity=1):
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

    Extensions:
    Fidelity of coverage - stop when fidelity level is covered by factors
    """
    U = set(cxt.object_attribute_pairs)
    len_initial = len(U)
    while (len_initial - len(U)) / len_initial < fidelity:
        D = set()
        V = 0
        to_remove = set()
        while True:
            D_objs = cxt.aprime(D)
            ls_measures = [(len(_oplus(D_objs, j, cxt, U)), j)
                           for j in set(cxt.attributes) - D]
            if ls_measures:
                maxDj = max(ls_measures, key=lambda x: x[0])
            else:
                maxDj = [0,]
            if maxDj[0] > V:
                j = maxDj[1]
                Dj = D | {j}
                C = cxt.aprime(Dj)
                D = cxt.oprime(C)
                to_remove = set(itertools.product(C, D)) & U
                V = len(to_remove)
            else:
                break
        if len(to_remove) == 0:
            print('Algorithm stuck, something went wrong, pairs left ', len(U))
            assert False
        U -= to_remove
        yield fca.Concept(C, D), len(to_remove) / len_initial


def algorithm2_weighted(cxt, fidelity=1):
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

    Extensions:
    Fidelity of coverage - stop when fidelity level is covered by factors
    """
    len_objs_initial = len(cxt.objects)
    len_atts_initial = len(cxt.attributes)

    def score(obj_att_pairs):
        objs = {x[0] for x in obj_att_pairs}
        atts = {x[1] for x in obj_att_pairs}
        score = len(objs) * len(atts) / (len_objs_initial * len_atts_initial)
        return score

    U = set(cxt.object_attribute_pairs)
    len_initial = len(U)
    while (len_initial - len(U)) / len_initial < fidelity:
        D = set()
        V = 0
        to_remove = set()
        while True:
            D_objs = cxt.oprime(D)
            ls_measures = [(score(_oplus(D_objs, j, cxt, U)), j)
                           for j in set(cxt.attributes) - D]
            if ls_measures:
                maxDj = max(ls_measures, key=lambda x: x[0])
            else:
                maxDj = [0,]
            if maxDj[0] > V:
                j_score, j = maxDj
                Dj = D | {j}
                C = cxt.aprime(Dj)
                D = cxt.oprime(C)
                to_remove = set(itertools.product(C, D)) & U
                V = len(to_remove)
            else:
                break
        if len(to_remove) == 0:
            print('Algorithm stuck, something went wrong, pairs left ', len(U))
            assert False
        U -= to_remove
        yield fca.Concept(C, D), j_score


def algorithm2_w_condition(cxt, fidelity: float = 1,
                           allow_repeatitions=True,
                           min_atts_and_objs=3, objs_ge_atts=False):
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

    :param objs_ge_atts: should the number of objects be greater or equal to
            the number of attributes in the output factors
    :param min_atts_and_objs: minimum number of attributes and objects in the
            output factors
    :param fidelity: stops when this fraction of crosses in the table are covered
    :param allow_repeatitions: exclude attributes in already obtained factors
            from further consideration - they still may appear in the closure
    """
    def good_factor(cpt: 'fca.Concept'):
        if objs_ge_atts:
            return len(cpt.extent) >= len(cpt.intent) >= min_atts_and_objs
        else:
            return len(cpt.extent) >= min_atts_and_objs and \
                   len(cpt.intent) >= min_atts_and_objs

    U = set(cxt.object_attribute_pairs)
    len_initial = len(U)
    removed_atts = set()
    if not len_initial:
        raise StopIteration
    while (len_initial - len(U)) / len_initial < fidelity:
        D = set()
        C = set()
        V = 0
        to_remove = set()
        available_atts = {x[1] for x in U} - removed_atts
        while True:
            Dprime = cxt.aprime(D)
            ls_measures = [(len(_oplus(Dprime, j, cxt, U)), j)
                           for j in available_atts - D]
            if not ls_measures:
                # print(f'Empty ls_measures. len(u) = {len(U)}')
                raise StopIteration
            # print('V=', V, ' ls_measures: ', ls_measures, '\nto_remove', to_remove)
            maxDj = max(ls_measures, key=lambda x: x[0])
            if (maxDj[0] < V and good_factor(cpt=fca.Concept(C, D))):  # yield factor
                if len(to_remove) == 0:
                    raise Exception(
                        f'Algorithm stuck, something went wrong, pairs left '
                        f'{len(U)}')
                if allow_repeatitions:
                    U -= to_remove
                else:
                    removed_atts |= {x[1] for x in to_remove}
                    # removed_objs |= {x[0] for x in to_remove}
                    U = {(o, a) for o, a in U
                         # if o not in removed_objs
                         if a not in removed_atts}
                # print(f'Good factor found: {len(C)}, {D}. len(U) = {len(U)}')
                yield fca.Concept(C, D), (len_initial - len(U)) / len_initial
                break
            else:  # update the values
                j_score, j = maxDj
                D_old = D.copy() | {j}
                Dj = D | {j}
                C = cxt.aprime(Dj)
                D = cxt.oprime(C)
                if len(D) == len(cxt.attributes) or (objs_ge_atts and len(C) < len(D)):
                    # removed_objs |= {x[0] for x in to_remove}
                    U = {(o, a) for o, a in U
                         # if o not in removed_objs
                         if a not in D_old}
                    # print(len(D) == len(cxt.attributes), objs_ge_atts, C, len(D), D_old)
                    # print(f'Dead end with {removed_atts}. len(u) = {len(U)}, {U}')
                    break
                to_remove = set(itertools.product(C, D)) & U
                V = len(to_remove)


if __name__ == '__main__':
    import cProfile
    import numpy.linalg as lalg
    from fca import make_random_context

    r_cxt = make_random_context(1200, 1000, .3)
    # r_cxt = r_cxt.reduce_attributes().reduce_objects()
    cProfile.run('print(lalg.svd(r_cxt.np_table))')
    cProfile.run('for x in algorithm2(r_cxt, .3): print(len(x[0].extent), len(x[0].intent), x[1])')
