# -*- coding: utf-8 -*-
"""
Holds functions for processing patterns. For this purpose one holds 2 contexts:
positive and negative. Patterns are combinations of attributes that only appear
in positive context and do not appear in the negative context.
Intuition: every pattern is a combination of attributes that is sufficient to
classify the respective object as positive.
"""
import copy

from fca import Concept
from fca.algorithms import factors


class PatternExplorationException(Exception):
    pass


class ContextMismatch(PatternExplorationException):
    pass


class AttributeMismatch(ContextMismatch):
    def __init__(self, pos_atts, neg_atts):
        self.pos_atts = pos_atts
        self.neg_atts = neg_atts

    def __str__(self):
        s = 'The positive attributes do not match the negative attributes'
        return s


class WrongNegativeExample(PatternExplorationException):
    pass


class NotNegativeExample(WrongNegativeExample):
    def __init__(self, intent, pattern):
        self.intent = intent
        self.pattern = pattern

    def __str__(self):
        out = "{0} is not a counter-example to {1}. ".format(self.intent,
                                                             self.pattern)
        out += "Negative example doesn't contain all attributes of the pattern"
        return out


class ConfirmedPatternsConflict(WrongNegativeExample):
    def __init__(self, obj_intent, pattern):
        self.intent = obj_intent
        self.conflicting_pattern = pattern

    def __str__(self):
        s = ('The attributes of the given example: {atts} '
             'conflict with the confirmed pattern: {pattern}'.format(
                atts=self.intent, pattern=self.conflicting_pattern))
        return s


class NotAPatternException(PatternExplorationException):
    def __init__(self, atts):
        self.atts = atts

    def __str__(self):
        s = 'A combination of attributes {atts} is not a pattern'.format(
            atts=self.atts
        )
        return s


class NotAPositivePattern(NotAPatternException):
    def __str__(self):
        s = 'A combination of attributes {atts} does ' \
            'not occur in the positive context'.format(
                atts=self.atts)
        return s


class NotANegativePattern(NotAPatternException):
    def __str__(self):
        s = 'A combination of attributes {atts} ' \
            'occurs in the negative context'.format(
                atts=self.atts)
        return s


def iterate_positive_concepts(positive_cxt, negative_cxt):
    reduced_pos_cxt = positive_cxt.reduce_attributes().reduce_objects()
    for cpt in reduced_pos_cxt.concepts:
        if negative_cxt.aclosure(cpt.intent) == set(
                negative_cxt.attributes):
            yield cpt


class BasicPatternExploration:

    def __init__(self, init_positive_cxt, init_negative_cxt,
                 expert=None, pattern_generator=iterate_positive_concepts):
        """
        :param init_positive_cxt:
        :param init_negative_cxt:
        :param expert: a function that returns negative examples to a given
            pattern
        :param pattern_generator: a function that takes positive and negative
            contexts and returns patterns
        """
        if set(init_positive_cxt.attributes) != set(init_negative_cxt.attributes):
            raise AttributeMismatch(init_positive_cxt.attributes,
                                    init_negative_cxt.attributes)
        self.positive_cxt = copy.deepcopy(init_positive_cxt)
        # self.positive_cpts = self.positive_cxt.concepts
        self.negative_cxt = copy.deepcopy(init_negative_cxt)
        # self.negative_cpts = self.negative_cxt.concepts
        self.expert = expert
        self.confirmed_patterns = set()
        self.pattern_generator = pattern_generator

    def iterate_patterns_with_examples(self):
        return self.pattern_generator(self.positive_cxt, self.negative_cxt)

    def get_unconfirmed_patterns_with_examples(self):
        unexplained_examples = list(self.iterate_unexplained_examples())
        out = []
        for pattern, freq in self.iterate_patterns_with_examples():
            if not self.is_explained(pattern):
                covered_examples = [example[0] for example in unexplained_examples
                                    if pattern <= example[1]]
                out.append((pattern, len(covered_examples)))
        return sorted(out, key=lambda x: -x[1])

    def confirm_pattern(self, pattern):
        if self.positive_cxt.aclosure(pattern) == set(self.positive_cxt.attributes):
            raise NotAPositivePattern(pattern)
        elif self.negative_cxt.aclosure(pattern) != set(self.negative_cxt.attributes):
            raise NotANegativePattern(pattern)
        self.confirmed_patterns.add(frozenset(pattern))
        return self

    def iterate_examples(self, pattern):
        obj_names = self.positive_cxt.aprime(pattern)
        examples = ((obj_name, self.positive_cxt.get_object_intent(obj_name))
                    for obj_name in obj_names)
        return examples

    def iterate_new_objects(self, pattern):
        for new_obj in self.expert(pattern):
            yield new_obj

    def add_negative_example(self, obj_name, obj_intent, pattern=None):
        if pattern is not None:
            if set(pattern) - set(obj_intent) != set():
                raise NotNegativeExample(obj_intent, pattern)
        self.negative_cxt.add_object_with_intent(obj_intent, obj_name)
        return self

    def add_positive_example(self, obj_name, obj_intent):
        self.positive_cxt.add_object_with_intent(obj_intent, obj_name)
        return self

    def is_explained(self, intent):
        return any(pattern <= set(intent)
                   for pattern in self.confirmed_patterns)

    def iterate_unexplained_examples(self):
        for obj_ind, obj_name in enumerate(self.positive_cxt.objects):
            obj_intent = self.positive_cxt.get_object_intent_by_index(obj_ind)
            if not self.is_explained(obj_intent):
                yield obj_name, obj_intent
