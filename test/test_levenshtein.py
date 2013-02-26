#!/usr/bin/env python
# -*- coding: utf-8 -*-

from levenshtein import levenshtein
from nose.tools import assert_less, assert_equal


args = dict(
    deletion_cost=100,
    insertion_cost=1,
    first_insertion_cost=50,
    prepend_first_insertion_cost=10,
    append_first_insertion_cost=5,
    substitution_cost=100
)


def test_first_insertion():
    for query, good, bad in [
        ('ab', 'abcc', 'acbc'),
        ('ab', 'abcc', 'acb'),
        ('men', 'mendeley', 'edmgen'),
        ('men', 'mendeley', 'metafun'),
        ('men', 'yamendeley', 'metafun'),
        ('men', 'mendeley', 'payment'),
        ('console', 'console2', 'QtConsole')
    ]:
        yield check_first_insertion, query, good, bad


def check_first_insertion(query, good, bad):
    assert_less(
        levenshtein(query, good, memo=[], precol=[], **args),
        levenshtein(query, bad, memo=[], precol=[], **args)
    )


def test_memo():
    whole = 'console'
    word = 'console2 '
    memo = []
    precol = []
    query = ''
    for ch in whole:
        assert_equal(
            levenshtein(query, word, memo=memo, precol=precol, **args),
            levenshtein(query, word, memo=[], precol=[], **args),
            query
        )
        query += ch
