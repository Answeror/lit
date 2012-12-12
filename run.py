#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from common import LitPlugin, LitJob, Worker
from utils import Query
import win32api
from PyQt4.QtGui import (
    QFileIconProvider,
    QIcon
)
from PyQt4.QtCore import (
    Qt,
    QThread,
    QMutex,
    QMutexLocker,
    QFileInfo,
    QAbstractListModel,
    Signal,
    QModelIndex,
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

    def __init__(self, name, path, query, worker):
        self.super.__init__()
        self.name = name
        self.path = path
        self.query = query
        self.worker = worker
        self._icon = None

    @property
    def super(self):
        return super(Runnable, self)

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
        self.super.__init__()
        self.items = items
        for i, item in enumerate(self.items):
            index = self.index(i, 0)
            item.icon_loaded.connect(lambda: self.dataChanged.emit(index, index))

    @property
    def super(self):
        return super(RunnableModel, self)

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


class Run(LitPlugin):

    def __init__(self):
        self.super.__init__()
        self.d = dict()
        self.worker = Worker()
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
                                ),
                                worker=self.worker
                            )

        self.mutex = QMutex()
        self.worker.run()

    @property
    def super(self):
        return super(Run, self)

    @property
    def name(self):
        return 'r'

    def lit(self, query, upper_bound, *args, **kargs):
        return Job(self.d, self.mutex, query, upper_bound)

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

            def f(executable):
                """Don't calculate editing distance if job stopped."""
                if self.stopped:
                    return 0
                return executable.query.distance_to(executable.name.lower())

            model = RunnableModel(sorted(self.d.values(), key=f)[:self.upper_bound])

        if self.done and not self.stopped:
            self.done(model)

    def __call__(self):
        self.run()

    def set_done_handle(self, done):
        self.done = done

    @property
    def finished(self):
        return self.isFinished()
