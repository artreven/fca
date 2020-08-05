# -*- coding: utf-8 -*-
"""
Holds class for context
"""
import copy
import logging
import random
from collections import Counter

import fca.algorithms

import numpy as np
from functools import reduce

module_logger = logging.getLogger(__name__)

####Exceptions
class ContextException(Exception):
    pass

class NotTableException(ContextException):
    def __init__(self, table):
        self.table = table
        
    def __str__(self):
        message = "The first parameter:\n{}".format(self.table)
        message += "\nis not convertible to lists of lists."
        return message

class NotContextException(ContextException):
    def __str__(self):
        return "Not a context, but should be."
    
class MultiplicationException(ContextException):
    def __init__(self, cxt_l, cxt_r):
        self.atts_num_l = len(cxt_l.attributes)
        self.objs_num_r = len(cxt_r.objects)
        
    def __str__(self):
        message = "Attributes of the first context:\n".format(self.atts_num_l)
        message += "\nand number of objects of the second context:\n".format(self.objs_num_r)
        message += "\nshould be the same."
        return message
    
class NotUniqueElementException(ContextException):
    def __init__(self, element):
        self.element = element
        
    def __str__(self):
        message = 'Element {} '.format(self.element)
        message += 'is already in context (object or attribute).'
        return message

class IncorrectElementException(ContextException):
    pass

class IncorrectAttributeException(IncorrectElementException):
    def __init__(self, att, cxt_atts):
        self.att = att
        self.cxt_atts = cxt_atts

    def __str__(self):
        out = 'Attribute {att} is not among context attributes.'.format(
            att=self.att)
        return out

####Decorators
def memo(f):
    """
    Decorator that caches the return value for each call to f(args).
    Then when called again with same args, we can just look it up.
    """
    def _f(*args):
        try:
            return _f.cache[args]
        except KeyError:
            _f.cache[args] = result = f(*args)
            return result
        except TypeError:
            # some element of args can't be a dict key
            return f(*args)
    _f.__name__ = f.__name__
    _f.cache = {}
    return _f


def clear_cxt_vars(cxt):
    """
    Clear all necessary context-class instance variables due to context change
    """
    if hasattr(cxt, '_cl'):
        del cxt._cl
    if hasattr(cxt, '_pairs'):
        del cxt._pairs


def basis_computation(f):
    def _f(*args, **kwargs):
        old_obj_intent = args[0].get_object_intent_by_index 
        old_att_extent = args[0].get_attribute_extent_by_index
        args[0].get_object_intent_by_index = memo(args[0].get_object_intent_by_index)
        args[0].get_attribute_extent_by_index = memo(args[0].get_attribute_extent_by_index)
        result = f(*args, **kwargs)
        del args[0].get_attribute_extent_by_index.cache
        del args[0].get_object_intent_by_index.cache
        args[0].get_object_intent_by_index = old_obj_intent
        args[0].get_attribute_extent_by_index = old_att_extent
        return result
    _f.__name__ = f.__name__
    return _f


def objects_attributes_change(f):
    """
    Decorator that clears context values when objects or attributes are modified.
    """
    def _f(*args):
        clear_cxt_vars(args[0])
        f(*args)
    return _f


####Context Class
class Context(object):
    """
    A Formal Context consists of two sets: *objects* and *attributes*
    and of a binary relation between them.

    As a data type we use a bit matrix.
    
    @note: refactored by Artem Revenko to increase performance.

    Examples
    ========

    Create a context.

    >>> ct = [[True, False, False, True],\
              [True, False, True, False],\
              [False, True, True, False],\
              [False, True, True, True]]
    >>> objs = [1, 2, 3, 4]
    >>> attrs = ['a', 'b', 'c', 'd']
    >>> c = Context(ct, objs, attrs)
    >>> c[0][0]
    True
    >>> c[0][2]
    False
    >>> 1 in c.objects
    True
    >>> 'f' in c.attributes
    False
    >>> for o in c:
    ...     print o
    ...     break
    ...
    [True, False, False, True]
    >>> transposed_c = c.transpose()
    >>> for o in transposed_c:
    ...     print o
    ...
    [True, True, False, False]
    [False, False, True, True]
    [False, True, True, True]
    [True, False, False, True]

    Class emulates container type.

    >>> len(c)
    4
    >>> c[1]
    [True, False, True, False]

    Usage of examples.

    >>> c.get_object_intent_by_index(1)
    set(['a', 'c'])
    >>> for ex in c.examples():
    ...     print ex
    ...     break
    ...
    set(['a', 'd'])
    
    Implications basis
    
    >>> for imp in c.attribute_implications:
    ...     print imp
    ...
    c, d => b
    b => c
    a, c, b => d
    
    >>> for imp in c.object_implications:
    ...     print imp
    ...
    3 => 4
    2, 4 => 3
    1, 3, 4 => 2
    """

    def __init__(self, cross_table=None, objects=None, attributes=None):
        """Create a context from cross table and list of objects, list
        of attributes
        
        cross_table - the list of bool lists
        objects - the list of objects
        attributes - the list of attributes 
        """
        # if not (isinstance(cross_table, list) and
        #         all(isinstance(i, list) for i in cross_table)):
        #     try:
        #         cross_table = [list(i) for i in cross_table]
        #     except:
        #         raise NotTableException(cross_table)
        if len(cross_table) != len(objects):
            raise ValueError("Number of objects (=%i) and number of cross table"
                   " rows(=%i) must agree" % (len(objects), len(cross_table)))
        elif (len(cross_table) != 0) and len(cross_table[0]) != len(attributes):
            raise ValueError("Number of attributes (=%i) and number of cross table"
                    " columns (=%i) must agree" % (len(attributes),
                        len(cross_table[0])))
        _attributes = attributes[:]
        if len(set(attributes)) < len(attributes):
            for att in _attributes:
                if _attributes.count(att) > 1:
                    indices = [i for i, x in enumerate(_attributes) if x == att]
                    for i in indices:
                        _attributes[i] = str(att) + '_{}'.format(i)
                    message =  "Not unique name of attribute '{}', ".format(att)
                    message += "renamed to '{}_n', n \in {}".format(att, indices)
                    module_logger.info(message)
        _objects = objects[:]
        if len(set(objects)) < len(objects):
            for obj in _objects:
                if _objects.count(obj) > 1:
                    indices = [i for i, x in enumerate(_objects) if x == obj]
                    for i in indices:
                        _objects[i] = str(obj) + '_{}'.format(i)
                    message =  "Not unique name of object '{}', ".format(obj)
                    message += "renamed to '{}_n', n \in {}".format(obj, indices)
                    module_logger.info(message)

        self._objects = _objects
        self._attributes = _attributes
        self.np_table = np.array(cross_table, dtype=bool)
        self.cross_table = self.np_table.tolist()
        self.object_indices = {obj: ind for ind, obj in enumerate(_objects)}
        self.attribute_indices = {att: ind
                                  for ind, att in enumerate(_attributes)}
        
    def get_table(self):
        return self.np_table
    table = property(get_table)
    
    def get_attributes(self):
        return self._attributes
    attributes = property(get_attributes)
    
    def get_objects(self):
        return self._objects
    objects = property(get_objects)
        
    def __deepcopy__(self, memo):
        return Context(copy.deepcopy(self.table, memo),
                       self.objects[:],
                       self.attributes[:])
        
    def get_concept_lattice(self):
        return fca.ConceptLattice(self)
    
    concept_lattice = property(get_concept_lattice)
    
    def get_concepts(self):
        return fca.algorithms.norris(self, False)
        
    concepts = property(get_concepts)

    def iterate_concepts(self):
        return fca.algorithms.iterative_norris(self)
        
    @basis_computation
    def get_attribute_canonical_basis(self,
                    get_basis=fca.algorithms.aibasis.compute_canonical_basis):
        """Compute the canonical implication basis on attributes"""
        return get_basis(self)
    
    def attribute_implications_iter(self):
        return self.get_attribute_implications(basis=fca.algorithms.dg_basis_iter_simple,
                                               confirmed=[],
                                               cond=lambda x: True)
    
    @basis_computation
    def get_attribute_implications(self, 
                                   basis=fca.algorithms.compute_dg_basis,
                                   confirmed=[],
                                   cond=lambda x: True):
        return basis(self, imp_basis=confirmed, cond=cond)
        # if not self._attr_imp_basis or (confirmed != self._confirmed):
        #             self._attr_imp_basis = basis(self, imp_basis=confirmed)
        #             self._confirmed = confirmed
        #         return self._attr_imp_basis
    
    _attr_imp_basis = None
    _confirmed = None
    attribute_implications = property(get_attribute_implications)
    
    @basis_computation
    def get_object_implications(self, 
                                basis=fca.algorithms.compute_dg_basis,
                                confirmed=None):
        cxt = self.transpose()
        if not self._obj_imp_basis:
            self._obj_imp_basis = basis(cxt, imp_basis=confirmed)
        return self._obj_imp_basis
    
    _obj_imp_basis = None
    object_implications = property(get_object_implications)
        
    def examples(self):
        """
        Generator. Generate set of corresponding attributes
        for each row (object) of context.
        """
        for obj_ind in range(len(self.objects)):
            yield self.get_object_intent_by_index(obj_ind)
            
    def intents(self):
        return self.examples()
    
    def get_object_intent_by_index(self, i):
        """
        Return a set of corresponding attributes for row with index i.
        """
        obj_row = self.np_table[i, :]
        att_inds = obj_row.nonzero()[0]
        atts = [self.attributes[j] for j in att_inds]
        return set(atts)
    
    def get_object_intent(self, o):
        index = self.object_indices[o]
        return self.get_object_intent_by_index(index)
    
    def get_attribute_extent_by_index(self, j):
        """
        Return a set of corresponding objects for column with index i.
        """
        att_col = self.np_table[:, j]
        obj_inds = att_col.nonzero()[0]
        objs = [self.objects[j] for j in obj_inds]
        return set(objs)
    
    def get_attribute_extent(self, a):
        index = self.attribute_indices[a]
        return self.get_attribute_extent_by_index(index)
        
    def get_value(self, o, a):
        io = self.objects.index(o)
        ia = self.attributes.index(a)
        return self[io][ia]

    def add_attribute(self, col, attr_name):
        """Add new attribute to context with given name"""
        # not optimised: not expected to be a usual operation
        new_table = np.c_[self.np_table, col]
        new_attributes = self.attributes + [attr_name]
        self.__init__(new_table, self.objects, new_attributes)

    def add_object(self, row, obj_name):
        """Add new object to context with given name

        @note: very slow, not suitable for incrementally creating a context"""
        # not optimised: not expected to be a usual operation
        if self.table.shape[0] > 0:
            new_table = np.vstack((self.table, [row]))
        else:
            new_table = np.array([row])
        new_objects = self.objects + [obj_name]
        self.__init__(new_table, new_objects, self.attributes)
        
    def add_object_with_intent(self, intent, obj_name):
        row = [(attr in intent) for attr in self.attributes]
        self.add_object(row, obj_name)
        
    def add_attribute_with_extent(self, extent, attr_name):
        col = [(obj in extent) for obj in self.objects]
        self.add_attribute(col, attr_name)

    def set_attribute_extent(self, extent, name):
        new_column = [False]*len(self.objects)
        for i in [self.object_indices[x] for x in extent]:
            new_column[i] = True
        self.np_table[:, self.attribute_indices[name]] = new_column
        new_table = self.np_table.tolist()
        self.__init__(new_table, self.objects, self.attributes)

    def set_object_intent(self, intent, name):
        new_row = [False]*len(self.attributes)
        for i in [self.attribute_indices[x] for x in intent]:
            new_row[i] = True
        self.table[self.object_indices[name]] = new_row
        self.__init__(self.table, self.objects, self.attributes)

    def delete_object(self, name):
        obj_index = self.object_indices[name]
        self.np_table = np.delete(self.np_table, obj_index, 0)
        new_table = self.np_table.tolist()
        del self.objects[obj_index]
        self.__init__(new_table, self.objects, self.attributes)

    def delete_attribute(self, name):
        att_index = self.attribute_indices[name]
        self.np_table = np.delete(self.np_table, att_index, 1)
        new_table = self.np_table.tolist()
        del self.attributes[att_index]
        self.__init__(new_table, self.objects, self.attributes)

    def delete_attributes(self, names):
        att_inds = [self.attribute_indices[name] for name in names]
        self.np_table = np.delete(self.np_table, att_inds, 1)
        new_table = self.np_table.tolist()
        for att_index in sorted(att_inds, reverse=True):
            del self.attributes[att_index]
        self.__init__(new_table, self.objects, self.attributes)

    def rename_object(self, old_name, name):
        self.objects[self.object_indices[old_name]] = name
        self.__init__(self.table, self.objects, self.attributes)

    def rename_attribute(self, old_name, name):
        self.attributes[self.attribute_indices[old_name]] = name
        self.__init__(self.table, self.objects, self.attributes)
        
    def oprime_inds(self, obj_inds):
        """
        Compute the set of all attributes shared by given objects. Objects
        are specified by indices.
        """
        if type(obj_inds) == set:
            obj_inds = list(obj_inds)
        try:
            common_intent = self.np_table[obj_inds[0], :].copy()
        except IndexError:
            return set(range(len(self.attributes)))
        else:
            for obj_ind in obj_inds[1:]:
                common_intent &= self.np_table[obj_ind, :]
            return common_intent.nonzero()[0]

    def aprime_inds(self, att_inds):
        """
        Compute the set of all objects shared by given attributes. Attributes
        are specified by indices.
        """
        if type(att_inds) == set:
            att_inds = list(att_inds)
        try:
            common_extent = self.np_table[:, att_inds[0]].copy()
        except IndexError:
            return set(range(len(self.objects)))
        else:
            for att_ind in att_inds[1:]:
                common_extent &= self.np_table[:, att_ind]
            return common_extent.nonzero()[0]

    def oclosure_inds(self, obj_inds):
        return self.aprime_inds(self.oprime_inds(obj_inds))

    def aclosure_inds(self, att_inds):
        return self.oprime_inds(self.aprime_inds(att_inds))
    
    def oprime(self, objects):
        obj_inds = [self.object_indices[obj] for obj in objects]
        att_inds = self.oprime_inds(obj_inds)
        return set(self.attributes[i] for i in att_inds)
    
    def aprime(self, attributes):
        att_inds = [self.attribute_indices[att] for att in attributes]
        obj_inds = self.aprime_inds(att_inds)
        return set(self.objects[i] for i in obj_inds)
    
    def oclosure(self, objects):
        obj_inds = [self.object_indices[obj] for obj in objects]
        closed_inds = self.oclosure_inds(obj_inds)
        return set(self.objects[i] for i in closed_inds)
    
    def aclosure(self, attributes):
        att_inds = [self.attribute_indices[att] for att in attributes]
        closed_inds = self.aclosure_inds(att_inds)
        return set(self.attributes[i] for i in closed_inds)

    def associative_aclosure(self, attributes):
        att_inds = [self.attribute_indices[att] for att in attributes]
        extent_inds = self.aprime_inds(att_inds)
        extent_size = len(extent_inds)
        associative_closure_inds = self.associative_oprime_inds(extent_inds)
        associative_closure = {self.attributes[ind]: associative_closure_inds[ind]
                               for ind in associative_closure_inds}
        return (associative_closure, extent_size)

    def associative_aprime(self, attributes):
        att_inds = [self.attribute_indices[att] for att in attributes]
        associative_aprime_inds = self.associative_aprime_inds(att_inds)
        associative_aprime = {self.objects[ind]: associative_aprime_inds[ind]
                              for ind in associative_aprime_inds}
        return associative_aprime

    def associative_oprime_inds(self, obj_inds):
        if type(obj_inds) == set:
            obj_inds = list(obj_inds)
        if len(obj_inds) == 0:
            return {att_ind: 0 for att_ind in range(len(self.attributes))}
        all_atts_list = []
        for obj_ind in obj_inds:
            all_atts_list += self.np_table[obj_ind, :].nonzero()[0].tolist()
        return Counter(all_atts_list)

    def associative_aprime_inds(self, att_inds):
        if type(att_inds) == set:
            att_inds = list(att_inds)
        if len(att_inds) == 0:
            return {obj_ind: 0 for obj_ind in range(len(self.objects))}
        all_objs_list = []
        for att_ind in att_inds:
            all_objs_list += self.np_table[:, att_ind].nonzero()[0].tolist()
        return Counter(all_objs_list)

    def transpose(self):
        """Return new context with transposed cross-table"""
        new_objects = self.attributes[:]
        new_attributes = self.objects[:]
        new_cross_table = []
        for j in range(len(self.attributes)):
            line = []
            for i in range(len(self.objects)):
                line.append(self.table[i][j])
            new_cross_table.append(line)
        return Context(new_cross_table, new_objects, new_attributes)
        
    def extract_subcontext_filtered_by_attributes(self, attributes_names,
                                                    mode="and"):
        """Create a subcontext with such objects that have given attributes"""
        values = dict( [(attribute, True) for attribute in attributes_names] )
        object_names, subtable = \
                            self._extract_subtable_by_attribute_values(values, mode)
        return Context(subtable,
                       object_names,
                       self.attributes)
                            
    def extract_subcontext(self, attribute_names):
        """Create a subcontext with only indicated attributes"""
        return Context(self._extract_subtable(attribute_names),
                       self.objects,
                       attribute_names)
        
    def get_object_attribute_pairs(self):
        pairs = [(self.objects[i], self.attributes[j])
                 for i, j in zip(*self.np_table.nonzero())]
        return pairs
    
    object_attribute_pairs = property(get_object_attribute_pairs)
    
    def remove_empty_objects(self):
        to_delete = []
        for i in range(len(self.objects)):
            if not any(self.table[i]):
                to_delete.append(self.objects[i])
        if to_delete:
            for i in to_delete:
                self.delete_object(i)
        return self

    def _extract_subtable(self, attribute_names):
        self._check_attribute_names(attribute_names)
        attribute_indices = [self.attributes.index(a) for a in attribute_names] 
        table = []
        for i in range(len(self)):
            row = []
            for j in attribute_indices:
                row.append(self[i][j])
            table.append(row)
        
        return table
        
    def _extract_subtable_by_condition(self, condition):
        """Extract a subtable containing only rows that satisfy the condition.
        Return a list of object names and a subtable.
        
        Keyword arguments:
        condition(object_index) -- a function that takes an an object index and
            returns a Boolean value
        
        """
        indices = [i for i in range(len(self)) if condition(i)]
        return ([self.objects[i] for i in indices],
                [self.table[i] for i in indices])
                
    def _extract_subtable_by_attribute_values(self, values, 
                                                    mode="and"):
        """Extract a subtable containing only rows with certain column values.
        Return a list of object names and a subtable.
        
        Keyword arguments:
        values -- an attribute-value dictionary
        
        """
        self._check_attribute_names(list(values.keys()))
        if mode == "and":
            indices = [i for i in range(len(self)) if self._has_values(i, values)]
        elif mode == "or":
            indices = [i for i in range(len(self)) if self._has_at_least_one_value(i, values)]
        return ([self.objects[i] for i in indices],
                [self.table[i] for i in indices])
                
    def _has_values(self, i, values):
        """Test if ith object has attribute values as indicated.
        
        Keyword arguments:
        i -- an object index
        values -- an attribute-value dictionary
        
        """
        for a in values:
            j = self.attributes.index(a)
            v = values[a]
            if self[i][j] != v:
                return False
        return True
        
    def _has_at_least_one_value(self, i, values):
        """Test if ith object has at least one attribute value as in values.
                
        Keyword arguments:
        i -- an object index
        values -- an attribute-value dictionary
        
        """
        for a in values:
            j = self.attributes.index(a)
            v = values[a]
            if self[i][j] == v:
                return True
        return False
            
    def _check_attribute_names(self, attribute_names):
        if not set(attribute_names) <= set(self.attributes):
            wrong_attributes = ""
            for a in set(attribute_names) - set(self.attributes):
                wrong_attributes += "\t%s\n" % a
            raise ValueError("Wrong attribute names:\n%s" % wrong_attributes)    

    ############################
    # Emulating container type #
    ############################

    def __len__(self):
        return len(self.table)

    def __getitem__(self, key):
        return self.table[key]

    ############################
    
    def __repr__(self):
        output = ", ".join(map(str, self.attributes)) + "\n"
        objects_list = list(map(str, self.objects))
        cross = {True : "X", False : "."}
        for i in range(len(self.objects)):
            output += (objects_list[i] + "\t" + 
                       "".join([cross[b] for b in self[i]]) + "\n")
        return output
    
    def __eq__(self, other):
        if type(other) != Context:
            raise TypeError("An input object should be a context!")
        if self.__repr__() == other.__repr__():
            return True
        elif (len(self.objects) != len(other.objects) or
              len(self.attributes) != len(other.attributes)):
            return False
        elif (set(self.objects) != set(other.objects) or
              set(self.attributes) != set(other.attributes)):
            return False
        else:
            obj_inds = [other.objects.index(obj) for obj in self.objects]
            att_inds = [other.attributes.index(att) for att in self.attributes]
            table = [[other.table[obj_inds[i]][att_inds[j]]
                      for j in range(len(self.attributes))]
                     for i in range(len(self.objects))]
            if table == self.cross_table:
                return True
            else:
                return False
    
    def __mul__(self, cxt_r):
        if not self.attributes == cxt_r.objects:
            raise MultiplicationException(self, cxt_r)
        new_objs = self.objects
        new_atts = cxt_r.attributes
        new_table = (np.matrix(self.table, dtype='bool') *
                     np.matrix(cxt_r.table, dtype='bool')).tolist()
        return Context(new_table, new_objs, new_atts)
    
    def clarify_objects(self):
        """
        Objects clarification
        Objects with intent equal to all attributes are not deleted.
        
        @return: clarified context
        @note: original context remains unchanged
        @note: may change the order of objects
        """        
        dict_cxt = dict(list(zip(list(map(tuple, self)), self.objects)))
        table = list(map(list, list(dict_cxt.keys())))
        objects = list(dict_cxt.values())
        return Context(table, objects, self.attributes)
        
    def reduce_objects(self):
        """
        Objects reducing.
        
        @return: reduced context
        @note: original context remains unchanged
        """        
        def int_repr(arr):
            """
            Represent every object's intent as decimal number
            """
            return list(map(list2int, arr))
        
        dict_cxt = dict(list(zip(int_repr(self), list(range(len(self))))))#clarification
        keys = list(dict_cxt.keys())
        reducible = set()
        M = (1 << len(self.attributes)) - 1              #set of attributes repr
        for i in range(len(keys)):                      #checking if i reducible
            if i in reducible:
                continue 
            rest = keys[:i] + keys[i+1:]
            current = new = M
            for j in rest:
                if j in reducible:
                    continue
                i_int = keys[i]
                new = current & j
                if new & i_int < i_int:
                    continue
                elif new == i_int:
                    reducible.add(i_int)
                elif new > i_int:
                    current = new
        for i in reducible:
            del dict_cxt[i]
        order = sorted(dict_cxt.values())
        objects = [self.objects[i] for i in order]
        table = [self[i] for i in order]
        return Context(table, objects, self.attributes)
    
    def reduce_attributes(self):
        """
        Attributes reducing.
        
        @note: relies on object reducing and context transposition
        """
        return self.transpose().reduce_objects().transpose()
    
    def complementary(self):
        """
        Make and return complementary context.
        
        @return: complementary context
        @note: original context remains unchanged
        """
        complementary_attributes = ['not ' + self.attributes[i]
                               for i in range(len(self.attributes))]
        complementary_table = []
        for i in range(len(self.objects)):
            complementary_table.append([not self.table[i][j]
                                   for j in range(len(self.attributes))])
        return Context(complementary_table, self.objects, complementary_attributes)
    
    def compound(self):
        """
        Make and return compound (= original + complementary) context.
        
        @return: compound context
        @note: original context remains unchanged
        """
        complementary_cxt = self.complementary() 
        compound_table = [self.table[i] + complementary_cxt.table[i]
                          for i in range(len(self.objects))]
        return Context(compound_table,
                       self.objects,
                       self.attributes + complementary_cxt.attributes)


def list2int(lst):
    """
    input lst - list of 1 and 0. Treat as binary number, make it decimal integer
    """
    def foo(x, y):
        return (x << 1) + y
    return reduce(foo, reversed(lst), 0)


def make_random_context(num_obj, num_att, d):
    """
    Make random context, useful for testing.
    
    @param d: density of the context, i.e. probability of finding a cross in any
    field.
    @param num_obj: number of object
    @param num_att: number of attributes  
    """
    obj_ls = ['g' + str(x) for x in range(num_obj)]
    att_ls = ['m' + str(x) for x in range(num_att)]
    table = [[int(d > random.random())
              for _ in range(num_att)]
             for _ in range(num_obj)]
    return Context(table, obj_ls, att_ls)

if __name__ == "__main__":
    """
    import doctest
    doctest.testmod()
    
    """
