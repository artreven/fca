'''
Use with Nosetests (https://nose.readthedocs.org/en/latest/)

Created on Jan 8, 2014

@author: artreven
'''
import numpy as np

import fca

class Test:

    def setUp(self):
        atts_num = 12
        objs_num = 60
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
        factors = fca.factors.algorithm2(self.cxt2)
        assert len(factors) == 2
        
    def test_factors2(self):
        factors = fca.factors.algorithm2(self.cxt_random)
        cxt_objs_fcts, cxt_fcts_atts = fca.factors.make_factor_cxts(factors)
        assert cxt_objs_fcts * cxt_fcts_atts == self.cxt_random.remove_empty_objects()
        
    def test_factors3(self):
        factors = fca.factors.algorithm2(self.cxt3)
        assert len(factors) == 4
        
    def test_make_factor_cxts(self):
        fct1 = fca.Concept(set(('g1', 'g3')), set(('m2', 'm1')))
        fct2 = fca.Concept(set(('g2',)), set(('m2', 'm3')))
        cxt_objs_fcts, cxt_fcts_atts = fca.factors.make_factor_cxts((fct1, fct2))
        assert cxt_objs_fcts == fca.Context([[1,0], [0,1], [1,0]],
                                            ['g1', 'g2', 'g3'],
                                            ['f0', 'f1'])
        assert cxt_fcts_atts == fca.Context([[1,1,0], [0,1,1]],
                                            ['f0', 'f1'],
                                            ['m1', 'm2', 'm3'])
        
    def test_oplus(self):
        D = set(('m3',))
        y = 'm2'
        assert (fca.factors._oplus(D, y, self.cxt1, set(self.cxt1.object_attribute_pairs)) ==
                set((('g1', 'm2'), ('g1', 'm3'))))
        D = set()
        y = 'm2'
        assert (fca.factors._oplus(D, y, self.cxt1, set(self.cxt1.object_attribute_pairs)) ==
                set((('g1', 'm2'), ('g3', 'm2'))))