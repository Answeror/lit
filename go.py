#!/usr/bin/env python
# -*- coding: utf-8 -*-

from common import LitPlugin, LitJob
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
import logging


Task = namedtuple('Task', 'hwnd query usetime')
WindowInfo = namedtuple('WindowInfo', 'name, hwnd, icon')


class WindowModel(QAbstractListModel):

    NAME_ROLE = Qt.DisplayRole
    HWND_ROLE = Qt.UserRole

    def __init__(self, items):
        self.super.__init__()
        self.items = items

    @property
    def super(self):
        return super(WindowModel, self)

    def rowCount(self, parent):
        return len(self.items)

    def columnCount(self, parent):
        return 1

    def data(self, index, role):
        if not index.isValid():
            return None
        if role == Qt.TextAlignmentRole:
            return int(Qt.AlignLeft | Qt.AlignVCenter)
        elif role == Qt.DisplayRole:
            return self.items[index.row()].name
        elif role == Qt.DecorationRole:
            return self.items[index.row()].icon
        elif role == Qt.UserRole:
            return self.items[index.row()].hwnd
        else:
            return None


class Go(LitPlugin):

    def __init__(self):
        self.tasks = {}
        self.mutex = QMutex()

    @property
    def name(self):
        return 'g'

    def lit(self, query, upper_bound, *args, **kargs):
        return Job(self, query, upper_bound)

    def _refresh_tasks(self, hwnds, query=None):
        for hwnd in hwnds:
            if not hwnd in self.tasks:
                self.tasks[hwnd] = Task(
                    hwnd=hwnd,
                    usetime=datetime.now(),
                    query=Query(
                        text='' if query is None else query,
                        insertion_cost=1,
                        deletion_cost=100,
                        substitution_cost=100,
                        transposition_cost=10
                    )
                )
            elif not query is None:
                self.tasks[hwnd].query.update(query.lower())

    def select(self, content, index):
        # check content type
        if not isinstance(content, WindowModel):
            logging.info('wrong content type {}'.format(type(content)))
            return

        for hwnd in _top_level_windows():
            if content.data(index, WindowModel.HWND_ROLE) == hwnd:
                self._refresh_tasks([hwnd])
                winutils.goto(hwnd=hwnd)
                return

        # remove invalid tasks
        del self.tasks[content.data(index, WindowModel.HWND_ROLE)]


class Job(LitJob, QThread):

    def __init__(self, go, query, upper_bound):
        LitJob.__init__(self)
        QThread.__init__(self)
        self.go = go
        self.done = None
        self.stopped = False
        self.query = query
        self.upper_bound = upper_bound

    def stop(self):
        self.stopped = True

    def sorted_active_runnable(self, query, hwnds):
        with QMutexLocker(self.go.mutex):
            # update query and collect active ones
            self.go._refresh_tasks(hwnds, query)
            active_tasks = hwnds >> sm.map(lambda h: self.go.tasks[h]) >> list

            # sort by last use
            if not query:
                return sorted(active_tasks, key=lambda t: t.usetime, reverse=True)

            def f(task):
                """Don't calculate editing distance if job stopped."""
                if self.stopped:
                    return 0
                return task.query.distance_to(_window_title(task.hwnd).lower())

            return sorted(active_tasks, key=f)

    def run(self):
        model = WindowModel(
            self.sorted_active_runnable(self.query, _top_level_windows())\
            >> sm.map(lambda t: WindowInfo(
                hwnd=t.hwnd,
                name=_window_title(t.hwnd),
                icon=winutils.get_window_icon(t.hwnd)
            ))\
            >> sm.item[:self.upper_bound]
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


def _top_level_windows():
    """ Returns the top level windows in a list of hwnds."""
    windows = []
    win32gui.EnumWindows(_window_enum_top_level, windows)
    return windows


def _window_title(hwnd):
    return win32gui.GetWindowText(hwnd)


def _window_enum_top_level(hwnd, windows):
    """ Window Enum function for getTopLevelWindows """
    #if win32gui.GetParent(hwnd) == 0 and title != '':
    if winutils.is_alt_tab_window(hwnd):
        windows.append(hwnd)
