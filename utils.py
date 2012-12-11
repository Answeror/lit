#!/usr/bin/env python
# -*- coding: utf-8 -*-


import stream as sm


def damerau_levenshtein_distance(
    s1,
    s2,
    deletion_cost=1,
    insertion_cost=1,
    substitution_cost=1,
    transposition_cost=1
):
    d = {}
    lenstr1 = len(s1)
    lenstr2 = len(s2)
    for i in range(-1,lenstr1+1):
        d[(i,-1)] = (i + 1) * deletion_cost
    for j in range(-1,lenstr2+1):
        d[(-1,j)] = min(j + 1, 1) * insertion_cost

    for i in range(lenstr1):
        best_before_insertion_cost = d[(i,-1)]
        for j in range(lenstr2):
            best_before_insertion_cost = min(best_before_insertion_cost, d[(i,j-1)])
            if s1[i] == s2[j]:
                cost = 0
            else:
                cost = 1
            d[(i,j)] = min(
                           d[(i-1,j)] + deletion_cost, # deletion
                           best_before_insertion_cost + insertion_cost, # insertion
                           d[(i-1,j-1)] + cost * substitution_cost, # substitution
                          )
            if i and j and s1[i]==s2[j-1] and s1[i-1] == s2[j]:
                d[(i,j)] = min (d[(i,j)], d[i-2,j-2] + cost * transposition_cost) # transposition

    return d[lenstr1-1,lenstr2-1]


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

    for i, c1 in enumerate(s1) >> sm.drop(len(a) - 1):
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
