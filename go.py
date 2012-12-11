#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lit import LitPlugin, LitJob
import win32gui
import windows as winutils
from datetime import datetime
from utils import Query
import stream as sm
from PyQt4.QtCore import (
    Qt,
    QAbstractListModel,
    QThread,
    QMutex,
    QMutexLocker
)
from collections import namedtuple


Runnable = namedtuple('Runnable', 'name hwnd icon query')


class WindowModel(QAbstractListModel):

    def __init__(self, names, icons):
        self.super.__init__()
        self.names = names
        self.icons = icons

    @property
    def super(self):
        return super(WindowModel, self)

    def rowCount(self, parent):
        return len(self.names)

    def columnCount(self, parent):
        return 1

    def data(self, index, role):
        if not index.isValid():
            return None
        if role == Qt.TextAlignmentRole:
            return int(Qt.AlignLeft | Qt.AlignVCenter)
        elif role == Qt.DisplayRole:
            return self.names[index.row()]
        elif role == Qt.DecorationRole:
            return self.icons[index.row()]
        else:
            return None


class Go(LitPlugin):

    def __init__(self):
        self.usetime = {}
        self.queries = {}
        self.mutex = QMutex()

    @property
    def name(self):
        return 'g'

    def lit(self, query, upper_bound, *args, **kargs):
        return Job(self.queries, self.mutex, query, upper_bound, self.usetime)

    def select(self, arg):
        for window in _getTopLevelWindows():
            if arg == window[1]:
                self.usetime[arg] = datetime.now()
                winutils.goto(window[0])
                return
        del self.usetime[arg]


class Job(LitJob, QThread):

    def __init__(self, queries, mutex, query, upper_bound, usetime):
        LitJob.__init__(self)
        QThread.__init__(self)
        self.queries = queries
        self.mutex = mutex
        self.done = None
        self.stopped = False
        self.query = query
        self.upper_bound = upper_bound
        self.usetime = usetime

    def stop(self):
        self.stopped = True

    def sorted_active_runnable(self, query, windows):
        with QMutexLocker(self.mutex):
            names = [w[1] for w in windows]

            # update use time
            for name in names:
                if not name in self.usetime:
                    self.usetime[name] = datetime.now()

            active_runnables = []

            # update query
            for hwnd, name in windows:
                if not name in self.queries or self.queries[name].hwnd != hwnd:
                    self.queries[name] = Runnable(
                        name=name,
                        hwnd=hwnd,
                        icon=winutils.get_window_icon(hwnd),
                        query=Query(
                            text=query,
                            insertion_cost=1,
                            deletion_cost=100,
                            substitution_cost=100,
                            transposition_cost=10
                        )
                    )
                else:
                    self.queries[name].query.update(query.lower())
                active_runnables.append(self.queries[name])

            # sort by last use
            if not query:
                return sorted(active_runnables, key=lambda r: self.usetime[r.name], reverse=True)

            def f(runnable):
                """Don't calculate editing distance if job stopped."""
                if self.stopped:
                    return 0
                return runnable.query.distance_to(runnable.name.lower())

            return sorted(active_runnables, key=f)

    def run(self):
        windows = _getTopLevelWindows()
        active_runnables = self.sorted_active_runnable(self.query, windows)[:self.upper_bound]
        model = WindowModel(
            active_runnables >> sm.map(lambda r: r.name) >> list,
            active_runnables >> sm.map(lambda r: r.icon) >> list
        )

        if self.done and not self.stopped:
            self.done(model)

    def __call__(self):
        self.run()

    def set_done_handle(self, done):
        self.done = done

    @property
    def finished(self):
        return self.isFinished()


def _getTopLevelWindows():
    """ Returns the top level windows in a list of tuples defined (HWND, title) """
    windows = []
    win32gui.EnumWindows(_windowEnumTopLevel, windows)
    return windows


def _windowEnumTopLevel(hwnd, windowsList):
    """ Window Enum function for getTopLevelWindows """
    title = win32gui.GetWindowText(hwnd)
    #if win32gui.GetParent(hwnd) == 0 and title != '':
    if winutils.is_alt_tab_window(hwnd):
        windowsList.append((hwnd, title))
