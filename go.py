#!/usr/bin/env python
# -*- coding: utf-8 -*-

from common import LitPlugin
import win32gui
import windows as winutils
from datetime import datetime
from utils import Query
from PyQt4.QtCore import (
    Qt,
    QAbstractListModel,
    QMutex,
    QMutexLocker,
    QObject
)
import itertools
import logging
from lcs import lcs


NAME_LIMIT = 42


class Task(object):

    def __init__(self, hwnd, query, usetime):
        self.hwnd = hwnd
        self.query = query
        self.usetime = usetime

    def use(self):
        self.usetime = datetime.now()

    @property
    def digest(self):
        if len(self.name) > NAME_LIMIT:
            shortname = self.name[:NAME_LIMIT - 3] + '...'
        else:
            shortname = self.name
        if self.filename:
            return '%s (%s)' % (shortname, self.filename)
        else:
            return shortname

    @property
    def title(self):
        return self.name

    @property
    def fullname(self):
        if self.filename:
            return self.title + self.filename
        else:
            return self.title

    @property
    def filename(self):
        if not hasattr(self, '_filename'):
            self._filename = winutils.get_app_name(self.hwnd)
        return self._filename

    @property
    def name(self):
        return _window_title(self.hwnd)

    @property
    def icon(self):
        if not hasattr(self, '_icon'):
            self._icon = winutils.get_window_icon(self.hwnd)
        return self._icon


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
            return self.items[index.row()].digest
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
        #winutils.elevate()

    @property
    def name(self):
        return 'g'

    def lit(self, query, upper_bound, worker, finished, *args, **kargs):
        worker.do(
            lambda: WindowModel(
                self.sorted_active_runnable(
                    query,
                    _top_level_windows()
                )[:upper_bound]
            ),
            finished=finished
        )

    def sorted_active_runnable(self, query, hwnds):
        with QMutexLocker(self.mutex):
            # update query and collect active ones
            self._refresh_tasks(hwnds, query)
            active_tasks = [self.tasks[h] for h in hwnds]

            # sort by last use
            if not query:
                return sorted(active_tasks, key=lambda t: t.usetime, reverse=True)

            titles = [task.fullname.lower() for task in active_tasks]

            def f(task, title):
                return task.query.distance_to(title)

            ds = [f(task, title) * (10 ** len(query)) for task, title in zip(active_tasks, titles)]
            best = ds[0]

            for i in itertools.takewhile(lambda i: ds[i] == best, range(len(ds))):
                ds[i] -= len(lcs(query, titles[i]))

            #return sorted(active_tasks, key=f)
            return [task for i, task in sorted(enumerate(active_tasks), key=lambda i: ds[i[0]])]

    def _refresh_tasks(self, hwnds, query=None):
        for hwnd in hwnds:
            if not hwnd in self.tasks:
                self.tasks[hwnd] = Task(
                    hwnd=hwnd,
                    usetime=datetime.now(),
                    query=Query(
                        text='' if query is None else query,
                        insertion_cost=1,
                        first_insertion_cost=50,
                        prepend_first_insertion_cost=5,
                        append_first_insertion_cost=10,
                        deletion_cost=100,
                        substitution_cost=100,
                        transposition_cost=10
                    )
                )
            elif not query is None:
                self.tasks[hwnd].query.update(query.lower())

    def update_usetime(self, hwnd):
        """Update with one time delay."""
        if hasattr(self, 'after_select') and self.after_select:
            self.after_select()
        self.after_select = self.tasks[hwnd].use

    def select(self, content, index):
        # check content type
        if not isinstance(content, WindowModel):
            logging.info('wrong content type {}'.format(type(content)))
            return

        for hwnd in _top_level_windows():
            if content.data(index, WindowModel.HWND_ROLE) == hwnd:
                self._refresh_tasks([hwnd])
                winutils.goto(hwnd=hwnd)
                self.update_usetime(hwnd)
                return

        # remove invalid tasks
        del self.tasks[content.data(index, WindowModel.HWND_ROLE)]


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
