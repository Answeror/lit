#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from utils import Query
from PyQt4.QtCore import (
    Qt,
    QAbstractListModel,
    QMutex,
    QMutexLocker
)
import itertools
import logging
from lcs import lcs
import windows


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
            self._filename = windows.get_app_name(self.hwnd)
        return self._filename

    @property
    def name(self):
        return windows.window_title(self.hwnd)

    @property
    def icon(self):
        if not hasattr(self, '_icon'):
            self._icon = windows.get_window_icon(self.hwnd)
        return self._icon


class WindowModel(QAbstractListModel):

    NAME_ROLE = Qt.DisplayRole
    HWND_ROLE = Qt.UserRole

    def __init__(self, client, items):
        super(WindowModel, self).__init__()
        self.client = client
        self.items = items

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

    def removeRows(self, row, count, parent):
        try:
            self.beginRemoveRows(parent, row, row + count - 1)
            for i in range(row, row + count):
                self.client.close_window(self.items[i].hwnd)
            self.items = self.items[:row] + self.items[row + count:]
            self.endRemoveRows()
        except Exception as e:
            logging.exception(e)
            return False
        else:
            return True


class Go(object):

    def __init__(self, worker, client):
        self.tasks = {}
        self.mutex = QMutex()
        self.worker = worker
        self.client = client

    @property
    def name(self):
        return 'g'

    def lit(self, query, upper_bound, finished, *args, **kargs):
        self.worker.do(
            make=lambda: WindowModel(
                self.client,
                self.sorted_active_runnable(
                    query,
                    windows.top_level_windows()
                )[:upper_bound]
            ),
            catch=finished,
            main=True
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
                        prepend_first_insertion_cost=10,
                        append_first_insertion_cost=5,
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

        for hwnd in windows.top_level_windows():
            if content.data(index, WindowModel.HWND_ROLE) == hwnd:
                self._refresh_tasks([hwnd])
                self.client.goto(hwnd=hwnd)
                self.update_usetime(hwnd)
                return

        # remove invalid tasks
        del self.tasks[content.data(index, WindowModel.HWND_ROLE)]
