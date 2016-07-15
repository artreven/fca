"""
Use with Nosetests (https://nose.readthedocs.org/en/latest/)

Created on Jan 8, 2014

@author: artreven
"""
import numpy as np

import fca

class Test:

    def setUp(self):
        atts_num = 20
        objs_num = 1500
        self.cxt_random = fca.make_random_context(objs_num, atts_num, 0.3)
        self.cxt1 = fca.Context([(0,1,1), (1,0,1), (0,1,0)],
                                ['g1', 'g2', 'g3'],
                                ['m1', 'm2', 'm3'])
        self.cxt2 = fca.Context([(0,1,1), (1,0,1), (0,1,1)],
                                ['g1', 'g2', 'g3'],
                                ['m1', 'm2', 'm3'])
        self.cxt3 = fca.Context([[1,0,1,0,1,1],
                                 [0,0,1,0,0,0],
                                 [1,1,0,1,1,1],
                                 [0,0,1,0,0,1],
                                 [0,1,1,1,0,1]],
                                ['g1', 'g2', 'g3', 'g4', 'g5'],
                                ['m1', 'm2', 'm3', 'm4', 'm5', 'm6'])

    def tearDown(self):
        pass
    
    def test_factors1(self):
        factors = list(fca.factors.algorithm2(self.cxt2))
        assert len(factors) == 2
        
    def test_exact_factors_random(self):
        factors = [x[0] for x in list(fca.factors.algorithm2(self.cxt_random))]
        print('Exact', len(factors))
        cxt_objs_fcts, cxt_fcts_atts = fca.factors.make_factor_cxts(factors)
        assert cxt_objs_fcts * cxt_fcts_atts == self.cxt_random.remove_empty_objects()

    def test_exact_factors_reduced_random(self):
        cxt_random_reduced = self.cxt_random.reduce_attributes().reduce_objects()
        factors = [x[0] for x in list(fca.factors.algorithm2(cxt_random_reduced))]
        print('Exact reduced', len(factors), len(cxt_random_reduced))
        cxt_objs_fcts, cxt_fcts_atts = fca.factors.make_factor_cxts(factors)
        assert cxt_objs_fcts * cxt_fcts_atts == cxt_random_reduced

    def test_approximate_factors_random(self):
        fidelity = .9
        factors = [x[0] for x in list(fca.factors.algorithm2(self.cxt_random, fidelity))]
        print('Approximate', len(factors))
        cxt_objs_fcts, cxt_fcts_atts = fca.factors.make_factor_cxts(factors)
        restored_cxt = cxt_objs_fcts * cxt_fcts_atts
        # assert all(x in self.cxt_random.object_attribute_pairs
        #            for x in restored_cxt.object_attribute_pairs)
        assert (len(restored_cxt.object_attribute_pairs) /
                len(self.cxt_random.object_attribute_pairs)) >= fidelity
        
    def test_factors3(self):
        factors = list(fca.factors.algorithm2(self.cxt3))
        assert len(factors) == 4

    def test_make_factor_cxts(self):
        fct1 = fca.Concept({'g1', 'g3'}, {'m2', 'm1'})
        fct2 = fca.Concept({'g2'}, {'m2', 'm3'})
        cxt_objs_fcts, cxt_fcts_atts = fca.factors.make_factor_cxts((fct1, fct2))
        assert cxt_objs_fcts == fca.Context([[1,0], [0,1], [1,0]],
                                            ['g1', 'g2', 'g3'],
                                            ['f0', 'f1'])
        assert cxt_fcts_atts == fca.Context([[1,1,0], [0,1,1]],
                                            ['f0', 'f1'],
                                            ['m1', 'm2', 'm3'])
        
    def test_oplus(self):
        D = {'m3'}
        y = 'm2'
        assert (fca.factors._oplus(D, y, self.cxt1,
                                   set(self.cxt1.object_attribute_pairs)) ==
                {('g1', 'm2'), ('g1', 'm3')})
        D = set()
        y = 'm2'
        assert (fca.factors._oplus(D, y, self.cxt1,
                                   set(self.cxt1.object_attribute_pairs)) ==
                {('g1', 'm2'), ('g3', 'm2')})