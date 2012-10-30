#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import subprocess as sp
from lit import LitPlugin


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
        words = [re.escape(w) for w in query]
        query = '.*'.join(words)
        p = re.compile(query, flags=re.IGNORECASE)
        return [name for name, _ in self.d.items() if not p.search(name) is None]

    def select(self, name):
        if name in self.d:
            # use shell=True to make lnk valid
            sp.call(self.d[name], shell=True)
