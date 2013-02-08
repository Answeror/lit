#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from common import LitPlugin, LitJob
from utils import Query
import win32api
from qt.QtGui import (
    QFileIconProvider,
    QIcon
)
from qt.QtCore import (
    Qt,
    QThread,
    QMutex,
    QMutexLocker,
    QFileInfo,
    QAbstractListModel,
    Signal,
    QObject
)
import logging
import windows
import resources_rc


icon_provider = QFileIconProvider()


def _file_icon(path):
    return icon_provider.icon(QFileInfo(path))


class Runnable(QObject):

    icon_loaded = Signal()

    def __init__(self, name, path, query, worker, order):
        super(Runnable, self).__init__()
        self.name = name
        self.path = path
        self.query = query
        self.worker = worker
        self.order = order
        self._icon = None

    @property
    def icon(self):
        if self._icon is None:
            #QThreadPool.globalInstance().start(AsyncJob(self._fill_icon))
            #QTimer.singleShot(0, self._fill_icon)
            #self._icon = windows.get_file_icon(self.path)
            self.worker.do(self._fill_icon)
            self._icon = QIcon(':/unknown.png')
        return self._icon

    def _fill_icon(self):
        self._icon = windows.get_file_icon(self.path)
        self.icon_loaded.emit()


class RunnableModel(QAbstractListModel):

    NAME_ROLE = Qt.DisplayRole
    ICON_ROLE = Qt.DecorationRole

    def __init__(self, items):
        super(RunnableModel, self).__init__()
        self.items = items
        for i, item in enumerate(self.items):
            index = self.index(i, 0)
            # must use Qt.DirectConnection here, but why?
            item.icon_loaded.connect(
                lambda: self.dataChanged.emit(index, index),
                Qt.DirectConnection
            )

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
        else:
            return None


class Files(LitPlugin):

    def __init__(self):
        super(Files, self).__init__()
        self.d = dict()
        self.mutex = QMutex()

    def path_list_changed(self):
        """Update runnable list."""
        with QMutexLocker(self.mutex):
            runnables = []
            for order, path in enumerate(self.paths):
                name, _ = os.path.splitext(os.path.basename(path))
                if name in self.d:
                    runnables.append((name, Runnable(
                        name=name,
                        path=path,
                        query=self.d[name].query,
                        worker=self.worker,
                        order=order
                    )))
                else:
                    runnables.append((name, Runnable(
                        name=name,
                        path=path,
                        query=Query(
                            text='',
                            insertion_cost=1,
                            first_insertion_cost=50,
                            prepend_first_insertion_cost=5,
                            append_first_insertion_cost=10,
                            deletion_cost=100,
                            substitution_cost=100,
                            transposition_cost=10
                        ),
                        worker=self.worker,
                        order=order
                    )))
            self.d = dict(runnables)

    @property
    def paths(self):
        assert False, 'Not implemented.'

    def select(self, content, index):
        # check content type
        if not isinstance(content, RunnableModel):
            logging.info('wrong content type {}'.format(type(content)))
            return

        name = content.data(index, RunnableModel.NAME_ROLE)
        if name in self.d:
            try:
                win32api.ShellExecute(0, 'open', self.d[name].path, '', '', 1)
            except Exception as e:
                logging.error(e)

    def lit(self, query, upper_bound, worker, finished, *args, **kargs):
        """Use mutex to protect self.d."""
        with QMutexLocker(self.mutex):
            for runnable in self.d.values():
                runnable.query.update(self.query.lower())

            def f(runnable):
                """Don't calculate editing distance if job stopped."""
                if self.stopped:
                    return 0
                elif not self.query:
                    return runnable.order
                else:
                    return runnable.query.distance_to(runnable.name.lower())

            model = RunnableModel(sorted(self.d.values(), key=f)[:self.upper_bound])
            self._finished = not self.stopped
            return None if self.stopped else model
