# -*- coding: utf-8 -*-
"""
Holds class for context
"""
import copy
import random

import fca.algorithms


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

    def __init__(self, cross_table=[], objects=[], attributes=[]):
        """Create a context from cross table and list of objects, list
        of attributes
        
        cross_table - the list of bool lists
        objects - the list of objects
        attributes - the list of attributes 
        """
        if len(cross_table) != len(objects):
            raise ValueError("Number of objects (=%i) and number of cross table"
                   " rows(=%i) must agree" % (len(objects), len(cross_table)))
        elif (len(cross_table) != 0) and len(cross_table[0]) != len(attributes):
            raise ValueError("Number of attributes (=%i) and number of cross table"
                    " columns (=%i) must agree" % (len(attributes),
                        len(cross_table[0])))

        self.table = cross_table
        self.objects = objects
        self.attributes = attributes
        
    def __deepcopy__(self, memo):
        return Context(copy.deepcopy(self.table, memo),
                       self.objects[:],
                       self.attributes[:])
    
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
        for obj_ind in xrange(len(self.objects)):
            yield self.get_object_intent_by_index(obj_ind)
            
    def intents(self):
        return self.examples()
    
    def get_object_intent_by_index_old(self, i):
        """Return a set of corresponding attributes for row with index i"""
        # TODO: !!! Very inefficient. Avoid using
        attrs_indexes = filter(lambda j: self.table[i][j],
                               range(len(self.table[i])))
        return set([self.attributes[i] for i in attrs_indexes])
    
    @memo
    def get_object_intent_by_index(self, i):
        """
        Return a set of corresponding attributes for row with index i.
        @note: refactored by Artem Revenko to increase performance.  
        """
        atts = [self.attributes[j]
                for j in xrange(len(self.attributes))
                if self.table[i][j]]
        return set(atts)
    
    def get_object_intent(self, o):
        index = self.objects.index(o)
        return self.get_object_intent_by_index(index)
    
    def get_attribute_extent_by_index_old(self, j):
        """Return a set of corresponding objects for column with index i"""
        objs_indexes = filter(lambda i: self.table[i][j],
                              range(len(self.table)))
        return set([self.objects[i] for i in objs_indexes])
    
    @memo
    def get_attribute_extent_by_index(self, j):
        """
        Return a set of corresponding objects for column with index i.
        @note: refactored by Artem Revenko to increase performance. 
        """
        objects = [self.objects[i]
                   for i in xrange(len(self.objects))
                   if self.table[i][j]]
        return set(objects)
    
    def get_attribute_extent(self, a):
        index = self.attributes.index(a)
        return self.get_attribute_extent_by_index(index)
        
    def get_value(self, o, a):
        io = self.objects.index(o)
        ia = self.attributes.index(a)
        return self[io][ia]
    
    def get_aibasis(self):
        """Compute the canonical basis using ai algorithm"""
        return fca.algorithms.aibasis.compute_canonical_basis(self)
    
    def add_attribute(self, col, attr_name):
        """Add new attribute to context with given name"""
        for i in range(len(self.objects)):
            self.table[i].append(col[i])
        self.attributes.append(attr_name)
        self.get_object_intent_by_index.__func__.cache = {}

    def add_column(self, col, attr_name):
        """Deprecated. Use add_attribute."""
        print "Deprecated. Use add_attribute."
        self.add_attribute(col, attr_name)

    def add_object(self, row, obj_name):
        """Add new object to context with given name"""
        self.table.append(row)
        self.objects.append(obj_name)
        self.get_attribute_extent_by_index.__func__.cache = {}
        
    def add_object_with_intent(self, intent, obj_name):
        self._attr_imp_basis = None
        self.objects.append(obj_name)
        row = [(attr in intent) for attr in self.attributes]
        self.table.append(row)
        self.get_attribute_extent_by_index.__func__.cache = {}
        
    def add_attribute_with_extent(self, extent, attr_name):
        col = [(obj in extent) for obj in self.objects]
        self.add_attribute(col, attr_name)
        self.get_object_intent_by_index.__func__.cache = {}
        
    def set_attribute_extent(self, extent, name):
        attr_index = self.attributes.index(name)
        for i in range(len(self.objects)):
            self.table[i][attr_index] = (self.objects[i] in extent)
        self.get_attribute_extent_by_index.__func__.cache = {}
        self.get_object_intent_by_index.__func__.cache = {}
            
    def set_object_intent(self, intent, name):
        obj_index = self.objects.index(name)
        for i in range(len(self.attributes)):
            self.table[obj_index][i] = (self.attributes[i] in intent)
        self.get_attribute_extent_by_index.__func__.cache = {}
        self.get_object_intent_by_index.__func__.cache = {}
        
    def delete_object(self, obj_index):
        del self.table[obj_index]
        del self.objects[obj_index]
        self.get_attribute_extent_by_index.__func__.cache = {}
        self.get_object_intent_by_index.__func__.cache = {}
        
    def delete_object_by_name(self, obj_name):
        self.delete_object(self.objects.index(obj_name))
    
    def delete_attribute(self, attr_index):
        for i in range(len(self.objects)):
            del self.table[i][attr_index]
        del self.attributes[attr_index]
        self.get_attribute_extent_by_index.__func__.cache = {}
        self.get_object_intent_by_index.__func__.cache = {}
        
    def delete_attribute_by_name(self, attr_name):
        self.delete_attribute(self.attributes.index(attr_name))
        
    def rename_object(self, old_name, name):
        self.objects[self.objects.index(old_name)] = name
        self.get_attribute_extent_by_index.__func__.cache = {}
        self.get_object_intent_by_index.__func__.cache = {}
        
    def rename_attribute(self, old_name, name):
        self.attributes[self.attributes.index(old_name)] = name
        self.get_attribute_extent_by_index.__func__.cache = {}
        self.get_object_intent_by_index.__func__.cache = {}
        
    def transpose(self):
        """Return new context with transposed cross-table"""
        new_objects = self.attributes[:]
        new_attributes = self.objects[:]
        new_cross_table = []
        for j in xrange(len(self.attributes)):
            line = []
            for i in xrange(len(self.objects)):
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
        self._check_attribute_names(values.keys())
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
        objects_list = map(str, self.objects)
        cross = {True : "X", False : "."}
        for i in xrange(len(self.objects)):
            output += (objects_list[i] + "\t" + 
                       "".join([cross[b] for b in self[i]]) + "\n")
        return output
    
    def clarify_objects(self):
        """
        Objects clarification
        Objects with intent equal to all attributes are not deleted.
        
        @return: clarified context
        @note: original context remains unchanged
        @author: Artem Revenko
        """
        if type(self) != Context:
            raise TypeError("An input object should be a context!")
        
        dict_cxt = dict(zip(map(tuple, self), self.objects))
        table = map(list, dict_cxt.keys())
        objects = dict_cxt.values()
        return Context(table, objects, self.attributes)
        
    def reduce_objects(self):
        """
        Objects reducing.
        
        @return: reduced context
        @note: original context remains unchanged
        @author: Artem Revenko
        """
        if type(self) != Context:
            raise TypeError("An input object should be a context!")
        
        def int_repr(arr):
            """
            Represent every object's intent as decimal number as in list_to_number
            """
            return map(self._bool_list_bitvalue, arr)
        
        dict_cxt = dict(zip(int_repr(self), range(len(self))))#clarification
        keys = dict_cxt.keys()
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
        objects = [self.objects[i] for i in dict_cxt.values()]
        table = [self[i] for i in dict_cxt.values()]
        return Context(table, objects, self.attributes)
    
    def complementary(self):
        """
        Make and return complementary context.
        
        @return: complementary context
        @note: original context remains unchanged
        @author: Artem Revenko
        """
        complementary_attributes = ['not ' + self.attributes[i]
                               for i in xrange(len(self.attributes))]
        complementary_table = []
        for i in range(len(self.objects)):
            complementary_table.append([not self.table[i][j]
                                   for j in xrange(len(self.attributes))])
        return Context(complementary_table, self.objects, complementary_attributes)
    
    def compound(self):
        """
        Make and return compound (= original + complementary) context.
        
        @return: compound context
        @note: original context remains unchanged
        @author: Artem Revenko
        """
        complementary_cxt = self.complementary() 
        compound_table = [self.table[i] + complementary_cxt.table[i]
                          for i in xrange(len(self.objects))]
        return Context(compound_table,
                       self.objects,
                       self.attributes + complementary_cxt.attributes)
    
    def _bool_list_bitvalue(self, lst):
        """
        input lst - list of Trues and Falses. Translate them to 1s and 0s,
        then concatenate in binstring, then make it decimal integer
        """
        return int(''.join([str(int(i)) for i in lst]), 2)
    
def make_random_context(obj_num, att_num, d):
    """
    Make random context, useful for testing.
    
    @param d: density of the context, i.e. probability of finding a cross in any
    field.
    @param obj_num: number of object
    @param att_num: number of attributes  
    """
    obj_ls = map(lambda x: 'g' + str(x), range(obj_num))
    att_ls = map(lambda x: 'm' + str(x), range(att_num))
    table = [[int(d > random.random())
              for _ in xrange(att_num)]
             for _ in xrange(obj_num)]
    return Context(table, obj_ls, att_ls)

if __name__ == "__main__":
    """
    import doctest
    doctest.testmod()
    
    """
    import random
    import cProfile
    
    num_atts = 40
    num_objs = 500
    cxt = make_random_context(num_objs, num_atts, 0.3)
    def check_same():
        obj_ind = random.choice(range(num_objs))
        att_ind = random.choice(range(num_atts))
        assert (cxt.get_object_intent_by_index_old(obj_ind) ==
                cxt.get_object_intent_by_index(obj_ind))
    for _ in range(10):
        check_same()
        
    def get_obj_int_index0():
        obj_ind = random.choice(range(num_objs))
        cxt.get_object_intent_by_index_old(obj_ind)
    def get_obj_int_index():
        obj_ind = random.choice(range(num_objs))
        cxt.get_object_intent_by_index(obj_ind)
    print 'object original'
    cProfile.run('''for _ in range(1000): get_obj_int_index0()''')
    print 'objects new'
    cProfile.run('''for _ in range(1000): get_obj_int_index()''')
    
    def get_att_index_old():
        att_ind = random.choice(range(num_atts))
        cxt.get_attribute_extent_by_index_old(att_ind)
    def get_att_index():
        att_ind = random.choice(range(num_atts))
        cxt.get_attribute_extent_by_index(att_ind)
    print 'att original'
    cProfile.run('''for _ in range(1000): get_att_index_old()''')
    print 'att new'
    cProfile.run('''for _ in range(1000): get_att_index()''')
    