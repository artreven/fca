'''
Use with Nosetests (https://nose.readthedocs.org/en/latest/)

Created on May 22, 2014

@author: artreven
'''
import fca

def test_unit_implication():
    imp = fca.Implication(set((1,2,3)), set((4,)))
    uimp = fca.UnitImplication(imp.premise, imp.conclusion.pop())
    assert uimp == imp
        
def test_unit_conclusion():
    uimp = fca.UnitImplication(set((1,2,3)), set((4,5)))
    assert type(uimp.conclusion) != set