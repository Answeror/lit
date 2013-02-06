#!/usr/bin/env python
# -*- coding: utf-8 -*-

from levenshtein import levenshtein


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
        first_insertion_cost=1,
        prepend_first_insertion_cost=1,
        append_first_insertion_cost=1,
        substitution_cost=1,
        transposition_cost=1
    ):
        self.text = text
        self.deletion_cost = deletion_cost
        self.insertion_cost = insertion_cost
        self.first_insertion_cost = first_insertion_cost
        self.prepend_first_insertion_cost = prepend_first_insertion_cost
        self.append_first_insertion_cost = append_first_insertion_cost
        self.substitution_cost = substitution_cost
        self.transposition_cost = transposition_cost
        self.memo = []
        self.precol = []

    def update(self, text):
        # remove last common position to make insertion penalty work
        self.memo = self.memo[:_common_prefix_length(self.text, text)]
        self.precol = []
        self.text = text

    def distance_to(self, text):
        return levenshtein(
            self.text,
            text,
            deletion_cost=self.deletion_cost,
            insertion_cost=self.insertion_cost,
            first_insertion_cost=self.first_insertion_cost,
            prepend_first_insertion_cost=self.prepend_first_insertion_cost,
            append_first_insertion_cost=self.append_first_insertion_cost,
            substitution_cost=self.substitution_cost,
            transposition_cost=self.transposition_cost,
            memo=self.memo,
            precol=self.precol
        )


class TreeQuery(object):

    def __init__(
        self,
        tree,
        query,
        deletion_cost=1,
        insertion_cost=1,
        first_insertion_cost=1,
        substitution_cost=1,
        transposition_cost=1
    ):
        self.query = query
        self.deletion_cost = deletion_cost
        self.insertion_cost = insertion_cost
        self.first_insertion_cost = first_insertion_cost
        self.substitution_cost = substitution_cost
        self.transposition_cost = transposition_cost

        self.nodes = []

        def add(parent, tree):
            for name, child in tree.items():
                node = TreeQueryNode(text=name, tree=self, parent=parent)
                self.nodes.append(node)
                add(node, child)
        add(None, tree)

        self.update('')

    def update(self, query):
        for node in self.nodes:
            node.update(self.query, query)
        self.query = query

    def best(self, count):
        return sorted(self.nodes, key=lambda node: node())[:count]


class TreeQueryNode(object):

    def __init__(
        self,
        text,
        tree,
        parent=None
    ):
        self.text = text
        self.tree = tree
        self.parent = parent
        self.memo = []
        self.precol = []

    @property
    def path(self):
        names = []
        node = self
        while node:
            names.append(node.text)
            node = node.parent
        return reversed(names)

    def update(self, old, new):
        self.memo = self.memo[:_common_prefix_length(old, new) + 1]
        self.precol = [] if self.parent is None else [x[-1] for x in self.parent.memo]
        levenshtein(
            new,
            self.text,
            deletion_cost=self.tree.deletion_cost,
            insertion_cost=self.tree.insertion_cost,
            substitution_cost=self.tree.substitution_cost,
            transposition_cost=self.tree.transposition_cost,
            memo=self.memo,
            precol=self.precol
        )

    def __call__(self):
        return self.memo[len(self.tree.query)][-1]
