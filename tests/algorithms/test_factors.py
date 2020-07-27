"""
Use with Nosetests (https://nose.readthedocs.org/en/latest/)

Created on Jan 8, 2014

@author: artreven
"""
import re

import nose.tools

import fca


class TestFactors:

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
        print(cxt_objs_fcts)
        assert cxt_objs_fcts == fca.Context([[1,0], [0,1], [1,0]],
                                            ['g1', 'g2', 'g3'],
                                            ['f0', 'f1'])
        assert cxt_fcts_atts == fca.Context([[1,1,0], [0,1,1]],
                                            ['f0', 'f1'],
                                            ['m1', 'm2', 'm3'])
        
    def test_oplus(self):
        D = {'m3'}
        y = 'm2'
        D_objs = self.cxt1.aprime(D)
        assert (fca.factors._oplus(D_objs, y, self.cxt1,
                                   set(self.cxt1.object_attribute_pairs)) ==
                {('g1', 'm2'), ('g1', 'm3')})
        D = set()
        y = 'm2'
        D_objs = self.cxt1.aprime(D)
        assert (fca.factors._oplus(D_objs, y, self.cxt1,
                                   set(self.cxt1.object_attribute_pairs)) ==
                {('g1', 'm2'), ('g3', 'm2')})


class TestFactorsWCondition:

    def setUp(self):
        pass

        self.cxt1 = fca.Context([(0, 1, 1), (1, 0, 1), (0, 1, 0)],
                                ['g1', 'g2', 'g3'],
                                ['m1', 'm2', 'm3'])
        self.cxt2 = fca.Context([(0, 1, 1), (1, 0, 1), (0, 1, 1)],
                                ['g1', 'g2', 'g3'],
                                ['m1', 'm2', 'm3'])
        self.cxt3 = fca.Context([[1, 0, 1, 0, 1, 1],
                                 [0, 0, 1, 0, 0, 0],
                                 [1, 1, 0, 1, 1, 1],
                                 [0, 0, 1, 0, 0, 1],
                                 [0, 1, 1, 1, 0, 1]],
                                ['g1', 'g2', 'g3', 'g4', 'g5'],
                                ['m1', 'm2', 'm3', 'm4', 'm5', 'm6'])

    def tearDown(self):
        pass

    def test_random_cxt(self):
        atts_num = 20
        objs_num = 1500
        cxt_random = fca.make_random_context(objs_num, atts_num, 0.3)
        factors_iter = fca.algorithms.algorithm2_w_condition(
            cxt_random, fidelity=1, allow_repeatitions=False,
            min_atts_and_objs=3, objs_ge_atts=True)
        assert len(list(factors_iter)) > 1

    def test_cxt1(self):
        ct = [[1, 0, 0, 0], [0, 0, 0, 1]]
        atts = list('abcd')
        objs = [1, 2]
        cxt1 = fca.Context(ct, objs, atts)
        factors_iter = fca.algorithms.algorithm2_w_condition(
            cxt1, fidelity=1, allow_repeatitions=True,
            min_atts_and_objs=3, objs_ge_atts=True
        )
        with nose.tools.assert_raises(StopIteration):
            next(factors_iter)

    @nose.tools.timed(20)
    def test_cxt2(self):
        cxt2_str = """
        0	...........X...............................X..........
        1	.X.....X...X.......XX............XX......X......X.....
        2	XX.....XX..XX.X.X..X..XX...XX.X..X..XX.....X.....X....
        3	...........XX...X......X.....X...X.........XX.........
        4	.XX........XXX..X..X....X........XXX......XX..........
        5	.X.........XX..XX.XX...X.XX.X......X..X.....X..X...X..
        6	X....X.....XX..XX.XX......X.X..X.XX..X.....XXX.X...X..
        7	.X.X.X..XX.XXXXXX...X......X..XXXX..XX.XX.X...X..X..X.
        8	XXX.XX.....XX..XX.XXX.XX..X...X..X...X....X.XX.....X.X
        9	.XXX....XXXX.XX.X.X.....XX.X.X..X...X.XX......X..X....
        10	.X.X.XX.XXXX.XXXX.X.....XX.X.X.XX.......X.X..XX..X....
        11	.X.........X........X............X.........X..........
        12	...........X.....................X.........X......X...
        13	XXXXXX....XXX.XXX......XX..X...X....XX...XXX.XX..X..X.
        14	.XX.XX......XXXXX...X.XX.X.X..XX.X.XXX..X...XX.X..X.XX
        15	.X..XX.....XXXXXX......X...X..XX.X..XXX...X.XX.X.XXXXX
        16	.X...........X.......X...........X..............X.X...
        17	.................X...X...........X..............X.X...
        18	.................X...............X....................
        19	.X....X......X...X...X...........XX....XXX......X.....
        20	......X....X.............................X.X..........
        21	......XX...X........X....................X.X..........
        22	.X.........XX.......X.............X......X.X..........
        23	......XX.....X...................X....................
        """
        ct = []
        objs = []
        for line in cxt2_str.split('\n'):
            line = line.strip()
            if not line:
                continue
            line_match = re.match(r'(\d+)\s+([.X]+)', line)
            obj = line_match.group(1)
            cross_str = line_match.group(2)
            crosses = [c == 'X' for c in cross_str]
            ct.append(crosses)
            objs.append(obj)
        cxt2 = fca.Context(ct, objects=objs,
                           attributes=[f'a{i}' for i in range(len(ct[0]))])
        factors_iter = fca.algorithms.algorithm2_w_condition(
            cxt2, fidelity=1, allow_repeatitions=False,
            min_atts_and_objs=3, objs_ge_atts=False)
        for i, x in enumerate(factors_iter):
            print(x)
        assert i > 0