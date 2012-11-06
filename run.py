#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import subprocess as sp
from lit import LitPlugin
from utils import damerau_levenshtein_distance
import win32api


class Run(LitPlugin):

    def __init__(self):
        self.super.__init__()
        self.d = dict()
        for path in os.environ['PATH'].split(os.pathsep):
            path = os.path.expandvars(path)
            if os.path.exists(path):
                for filename in os.listdir(path):
                    name, ext = os.path.splitext(filename)
                    if ext in ['.exe', '.cmd', '.bat', '.lnk']:
                        if not name in self.d:
                            self.d[name] = os.path.join(path, filename)

    @property
    def super(self):
        return super(Run, self)

    @property
    def name(self):
        return 'r'

    def lit(self, query):
        query = query.lower()
        f = lambda name: damerau_levenshtein_distance(
            query,
            name.lower(),
            insertion_cost=1,
            deletion_cost=100,
            substitution_cost=100,
            transposition_cost=10
        )
        names = self.d.keys()
        return sorted(names, key=f)

    def select(self, name):
        if name in self.d:
            # use shell=True to make lnk valid
            #sp.call(self.d[name], shell=True)
            win32api.ShellExecute(0, 'open', self.d[name], '', '', 1)
