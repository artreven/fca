#!/usr/bin/env python
# encoding: utf-8

import unittest
from fca.algorithms import closure_operators
import fca
from fca import compute_dg_basis
from fca.implication import Implication


class BasisTest(unittest.TestCase):
    def setUp(self):
        objects = ['Air Canada', 'Air New Zeland', 'All Nippon Airways',
                   'Ansett Australia', 'The Australian Airlines Group',
                   'British Midland', 'Lufthansa', 'Mexicana',
                   'Scandinavian Airlines', 'Singapore Airlines',
                   'Thai Airways International', 'United Airlines',
                   'VARIG']
        attributes = ['Latin America', 'Europe', 'Canada', 'Asia Pasific',
                      'Middle East', 'Africa', 'Mexico', 'Carribean',
                      'United States']
        table = [[True, True, True, True, True, False, True, True, True],
                 [False, True, False, True, False, False, False, False, True],
                 [False, True, False, True, False, False, False, False, True],
                 [False, False, False, True, False, False, False, False, False],
                 [False, True, True, True, True, True, False, False, True],
                 [False, True, False, False, False, False, False, False, False],
                 [True, True, True, True ,True, True, True, False, True],
                 [True, False, True, False, False, False, True, True, True],
                 [True, True, False, True, False, True, False, False, True],
                 [False, True, True, True, True, True, False, False, True],
                 [True, True, False, True, False, False, False, True, True],
                 [True, True, True, True, False, False, True, True, True],
                 [True, True, False, True, False, True, True, False, True]]
        self.cxt = fca.Context(table, objects, attributes)

class AirlinesTest(BasisTest):
    def test_attribute_implications(self):
        self.attribute_implications = [
            Implication({'Carribean'},
                        {'United States', 'Carribean', 'Latin America'}),
            Implication({'Mexico'},
                        {'United States', 'Latin America', 'Mexico'}),
            Implication({'Africa'},
                        {'Europe', 'United States', 'Asia Pasific', 'Africa'}),
            Implication({'Middle East'},
                        {'Canada', 'Europe', 'Asia Pasific', 'United States',
                         'Middle East'}),
            Implication({'United States', 'Asia Pasific'},
                        {'Europe', 'United States', 'Asia Pasific'}),
            Implication({'Canada'}, {'Canada', 'United States'}),
            Implication({'Europe', 'United States'},
                        {'Europe', 'United States', 'Asia Pasific'}),
            Implication({'Europe', 'Asia Pasific'},
                        {'Europe', 'United States', 'Asia Pasific'}),
            Implication(
                {'Canada', 'Europe', 'Asia Pasific', 'Africa', 'United States'},
                {'Canada', 'Europe', 'Asia Pasific', 'Africa',
                         'United States', 'Middle East'}),
            Implication({'Latin America'},
                        {'United States', 'Latin America'}),
            Implication(
                {'United States', 'Carribean', 'Latin America', 'Mexico'},
                {'Canada', 'United States', 'Carribean',
                         'Latin America', 'Mexico'}),
            Implication({'Canada', 'United States', 'Latin America'},
                        {'Canada', 'United States', 'Latin America', 'Mexico'}),
            Implication({'Europe', 'Asia Pasific', 'Africa', 'United States',
                         'Carribean', 'Latin America'},
                        {'Canada', 'Europe', 'Asia Pasific', 'Mexico', 'Africa',
                         'United States', 'Middle East', 'Carribean',
                         'Latin America'}),
        ]
        
        imp_basis = compute_dg_basis(self.cxt)
        self.assertEqual(len(imp_basis), len(self.attribute_implications))
        for imp in self.attribute_implications:
            self.assertTrue(imp in imp_basis)
	        
class RelativeBasisTest(unittest.TestCase):
    def setUp(self):
        ct = [[True, False, False, True],
              [True, False, True, False],
              [False, True, True, False],
              [False, True, True, True]]
        objs = ['1', '2', '3', '4']
        attrs = ['a', 'b', 'c', 'd']
        self.cxt = fca.Context(ct, objs, attrs)
        self.basis = [Implication({'c', 'd'}, {'b'})]
    
    def test_relative_basis(self):
        simple_basis = compute_dg_basis(self.cxt)
        self.assertEqual(len(simple_basis), 3)
        relative_basis = compute_dg_basis(self.cxt, imp_basis=self.basis)
        self.assertEqual(len(set(relative_basis) & set(self.basis)), 0)
        self.assertEqual(len(relative_basis), 2)
        self.assertEqual(len(self.basis), 1)

class BasisTest2(unittest.TestCase):
    def setUp(self):
        ct = [[True, True, True, True],
              [True, False, True, False],
              [False, True, True, False],
              [False, True, True, True]]
        objs = ['1', '2', '3', '4']
        attrs = ['a', 'b', 'c', 'd']
        self.cxt = fca.Context(ct, objs, attrs)
    
    def test_relative_basis(self):
        imp_basis=[Implication(set(), {'c'})]
        relative_basis = compute_dg_basis(self.cxt, imp_basis=imp_basis)
        self.assertFalse(imp_basis[0] in relative_basis)

    def test_basis(self):
        simple_basis = compute_dg_basis(self.cxt)
        
        message = "Implication [{0}] occurs more than once"
        for imp1 in simple_basis:
            counter = 0
            for imp2 in simple_basis:
                if imp1 == imp2:
                    counter += 1
            self.assertEqual(counter, 1, message.format(imp1))

        
        


if __name__ == '__main__':
    unittest.main()