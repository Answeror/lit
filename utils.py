#!/usr/bin/env python
# -*- coding: utf-8 -*-


def levenshtein(
    s1,
    s2,
    deletion_cost=1,
    insertion_cost=1,
    substitution_cost=1,
    transposition_cost=1,
    memo=[]
):
    previous_row = 0
    a = memo

    if not a:
        a.append([i * insertion_cost for i in range(len(s2) + 1)])

    for i, c1 in list(enumerate(s1))[len(a) - 1:]:
        previous_row = i
        current_row = i + 1
        a.append([0 for i in range(len(s2) + 1)])
        a[current_row][0] = (i + 1) * deletion_cost
        for j, c2 in enumerate(s2):
            # j+1 instead of j since previous_row and current_row are one character longer
            insertions = a[current_row][j] + insertion_cost
            deletions = a[previous_row][j + 1] + deletion_cost
            substitutions = a[previous_row][j] + (c1 != c2) * substitution_cost
            a[current_row][j + 1] = min(insertions, deletions, substitutions)

    return a[len(s1)][-1]


def _common_prefix_length(s1, s2):
    for i, (c1, c2) in enumerate(zip(s1, s2)):
        if c1 != c2:
            return i
    return min(len(s1), len(s2))


class Query(object):

    def __init__(
        self,
        text,
        deletion_cost=1,
        insertion_cost=1,
        substitution_cost=1,
        transposition_cost=1
    ):
        self.text = text
        self.deletion_cost = deletion_cost
        self.insertion_cost = insertion_cost
        self.substitution_cost = substitution_cost
        self.transposition_cost = transposition_cost
        self.memo = []

    def update(self, text):
        self.memo = self.memo[:_common_prefix_length(self.text, text) + 1]
        self.text = text

    def distance_to(self, text):
        return levenshtein(
            self.text,
            text,
            deletion_cost=self.deletion_cost,
            insertion_cost=self.insertion_cost,
            substitution_cost=self.substitution_cost,
            transposition_cost=self.transposition_cost,
            memo=self.memo
        )
