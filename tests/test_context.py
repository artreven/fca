"""
Use with Nosetests (https://nose.readthedocs.org/en/latest/)

Created on Jan 8, 2014

@author: artreven
"""
import fca

class Test:

    def setUp(self):
        self.objs_num = 60
        self.atts_num = 12
        self.cxt_random = fca.make_random_context(self.objs_num, self.atts_num, 0.3)
        self.cxt1 = fca.Context([[1,1,0], [0,1,1], [0,0,1]],
                                ['g2', 'g1', 'g3'],
                                ['m1', 'm3', 'm2'])
        self.cxt2 = fca.Context([(0,1,1), (1,0,1), (0,1,0)],
                                ['g1', 'g2', 'g3'],
                                ['m1', 'm2', 'm3'])
        
    def tearDown(self):
        pass


    def test_attributes_change(self):
        self.cxt_random.get_object_intent_by_index(0)
        self.cxt_random.add_attribute([1] * self.objs_num, 'new_att')
        assert 'new_att' in self.cxt_random.get_object_intent_by_index(0)
        
        self.cxt_random.set_attribute_extent(set(), 'new_att')
        assert not 'new_att' in self.cxt_random.get_object_intent_by_index(0)
        
        self.cxt_random.set_attribute_extent(self.cxt_random.objects, 'new_att')
        self.cxt_random.delete_attribute('new_att')
        assert not 'new_att' in self.cxt_random.get_object_intent_by_index(0)
        
        self.cxt_random.add_attribute([1] * self.objs_num, 'new_att')
        self.cxt_random.rename_attribute('new_att', 'old_att')
        assert not 'new_att' in self.cxt_random.get_object_intent_by_index(0)
        assert 'old_att' in self.cxt_random.get_object_intent_by_index(0)
        
    def test_objects_change(self):        
        self.cxt_random.get_attribute_extent_by_index(0)
        self.cxt_random.add_object([1] * self.atts_num, 'new_obj')
        assert 'new_obj' in self.cxt_random.get_attribute_extent_by_index(0)
        
        self.cxt_random.set_object_intent([], 'new_obj')
        assert not 'new_obj' in self.cxt_random.get_attribute_extent_by_index(0)
        
        self.cxt_random.set_object_intent(self.cxt_random.attributes, 'new_obj')
        self.cxt_random.delete_object('new_obj')
        assert not 'new_obj' in self.cxt_random.get_attribute_extent_by_index(0)
        
        self.cxt_random.add_object([1] * self.atts_num, 'new_obj')
        self.cxt_random.rename_object('new_obj', 'old_obj')
        assert not 'new_obj' in self.cxt_random.get_attribute_extent_by_index(0)
        assert 'old_obj' in self.cxt_random.get_attribute_extent_by_index(0)
        
    def test_multiply(self):
        table_l = [[1,0,1,1],
                   [0,0,0,1],
                   [0,1,1,0],
                   [1,0,0,1],
                   [1,1,0,1]]
        cxt_l = fca.Context(table_l,
                            ['g1', 'g2', 'g3', 'g4', 'g5'],
                            ['f1', 'f2', 'f3', 'f4'])
        table_r = [[0,0,1,0,0,1],
                   [0,1,0,1,0,1],
                   [1,0,0,0,1,1],
                   [0,0,1,0,0,0]]
        cxt_r = fca.Context(table_r,
                            ['f1', 'f2', 'f3', 'f4'],
                            ['m1', 'm2', 'm3', 'm4', 'm5', 'm6'])
        table_o = [[1,0,1,0,1,1],
                   [0,0,1,0,0,0],
                   [1,1,0,1,1,1],
                   [0,0,1,0,0,1],
                   [0,1,1,1,0,1]]
        cxt_mult = cxt_l * cxt_r
        assert cxt_mult.table == table_o
        assert cxt_mult.objects == ['g1', 'g2', 'g3', 'g4', 'g5']
        assert cxt_mult.attributes == ['m1', 'm2', 'm3', 'm4', 'm5', 'm6']
        
    def test_eq(self):
        assert self.cxt1 == self.cxt2
        
    def test_get_object_attribute_pairs(self):
        assert self.cxt2.object_attribute_pairs == [('g1', 'm2'), ('g1', 'm3'),
                                                    ('g2', 'm1'), ('g2', 'm3'),
                                                    ('g3', 'm2')]
        
    def test_basis(self):
        assert len(self.cxt1.get_attribute_canonical_basis()) == 1
        imp = self.cxt1.get_attribute_canonical_basis()[0]
        assert str(imp) == "m1 => m3"
        assert len(self.cxt2.get_attribute_canonical_basis()) == 1
