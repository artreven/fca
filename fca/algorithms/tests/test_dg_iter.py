'''
Use with Nosetests (https://nose.readthedocs.org/en/latest/)

Created on Dec 23, 2014

@author: artreven
'''
import fca

def test_random_dg_iter():
    r_cxt = fca.make_random_context(40, 15, 0.3)
    dg_basis = r_cxt.get_attribute_implications()
    dg_basis_from_iter = [x for x in r_cxt.attribute_implications_iter()]
    assert len(dg_basis) == len(dg_basis_from_iter)