#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from lit import LitPlugin, LitJob
from utils import levenshtein
import win32api
from collections import namedtuple
import stream as sm
from PyQt4.QtCore import (
    QThread,
    QMutex,
    QMutexLocker
)


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


Runnable = namedtuple('Runnable', 'name path query')


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
                            self.d[name] = Runnable(
                                name=name,
                                path=os.path.join(path, filename),
                                query=Query(
                                    text='',
                                    insertion_cost=1,
                                    deletion_cost=100,
                                    substitution_cost=100,
                                    transposition_cost=10
                                )
                            )

        self.mutex = QMutex()

    @property
    def super(self):
        return super(Run, self)

    @property
    def name(self):
        return 'r'

    def lit(self, query, upper_bound, *args, **kargs):
        return Job(self.d, self.mutex, query, upper_bound)

    def select(self, name):
        if name in self.d:
            # use shell=True to make lnk valid
            #sp.call(self.d[name], shell=True)
            win32api.ShellExecute(0, 'open', self.d[name], '', '', 1)


class Job(LitJob, QThread):

    def __init__(self, d, mutex, query, upper_bound):
        LitJob.__init__(self)
        QThread.__init__(self)
        self.done = None
        self.stopped = False
        self.d = d
        self.mutex = mutex
        self.query = query
        self.upper_bound = upper_bound

    def stop(self):
        self.stopped = True

    def run(self):
        """Use mutex to protect self.d."""
        with QMutexLocker(self.mutex):
            for runnable in self.d.values():
                runnable.query.update(self.query.lower())

            def f(arg):
                """Don't calculate editing distance if job stopped."""
                if self.stopped:
                    return 0
                return arg[1].query.distance_to(arg[1].name.lower())

            names = sorted(self.d.items(), key=f)\
                    >> sm.apply(lambda name, _: name)\
                    >> sm.item[:self.upper_bound]

        if self.done and not self.stopped:
            self.done(names)

    def __call__(self):
        self.run()

    def set_done_handle(self, done):
        self.done = done

    @property
    def finished(self):
        return self.isFinished()
