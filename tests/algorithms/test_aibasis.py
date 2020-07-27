"""
Use with Nosetests (https://nose.readthedocs.org/en/latest/)

Created on Dec 17, 2013

@author: artreven
"""
import fca
import fca.algorithms

class Test:

    def setUp(self):
        self.cxt_random = fca.make_random_context(60, 12, 0.3) 

    def tearDown(self):
        pass

    def test_basis_length(self):
        aibasis = self.cxt_random.get_attribute_canonical_basis(
                      get_basis=fca.algorithms.aibasis.compute_canonical_basis)
        ncbasis = self.cxt_random.get_attribute_implications()
        assert (len(aibasis) == len(ncbasis)), (len(aibasis), len(ncbasis))
        
    def test_same_closure(self):
        aibasis = self.cxt_random.get_attribute_canonical_basis(
                      get_basis=fca.algorithms.aibasis.compute_canonical_basis)
        ncbasis = self.cxt_random.get_attribute_implications()
        for i in range(12):
            for j in range(12):
                attr_set = {'m' + str(i), 'm' + str(j)}
                assert (fca.algorithms.lin_closure(attr_set, aibasis) ==
                        fca.algorithms.lin_closure(attr_set, ncbasis))