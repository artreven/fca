"""
Use with Nosetests (https://nose.readthedocs.org/en/latest/)

Created on May 22, 2014

@author: artreven
"""
import fca

def test_unit_implication():
    imp = fca.Implication({1, 2, 3}, {4})
    uimp = fca.UnitImplication(imp.premise, imp.conclusion.pop())
    assert uimp == imp
