#!/usr/bin/env python
# -*- coding: utf-8 -*-


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
