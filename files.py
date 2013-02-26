#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from utils import Query
import win32api
from qt.QtGui import (
    QFileIconProvider,
    QIcon
)
from qt.QtCore import (
    Qt,
    QTimer,
    QMutex,
    QMutexLocker,
    QFileInfo,
    QAbstractListModel,
    Signal,
    Slot,
    QObject,
    QMetaObject,
    Q_ARG
)
import logging
import windows
from functools import partial
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
            self.worker.do(
                action=self._fill_icon,
                react=self._fill_icon_finished,
                main=True,
                priority=-42
            )
            return self._default_icon()
        else:
            return self._icon

    def _default_icon(self):
        return QIcon(':/unknown.png')

    def _fill_icon_finished(self):
        self.icon_loaded.emit()

    def _fill_icon(self):
        self._icon = windows.get_file_icon(self.path)
        if self._icon is None:
            self._icon = self._default_icon()


class UpdateIcon(QObject):

    def __init__(self, model, index):
        super(UpdateIcon, self).__init__(model)
        self.index = index

    @Slot()
    def fire(self):
        self.parent().dataChanged.emit(self.index, self.index)


class RunnableModel(QAbstractListModel):

    NAME_ROLE = Qt.DisplayRole
    ICON_ROLE = Qt.DecorationRole

    def __init__(self, items):
        super(RunnableModel, self).__init__()
        self.items = items
        for i, item in enumerate(self.items):
            # must use Qt.DirectConnection here, but why?
            update = UpdateIcon(self, self.index(i, 0))
            update.setParent(self)
            item.icon_loaded.connect(update.fire)
            self.destroyed.connect(partial(item.icon_loaded.disconnect, update.fire))

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


class Files(object):

    def __init__(self, worker, **kargs):
        super(Files, self).__init__()
        self.d = dict()
        self.mutex = QMutex()
        self.worker = worker

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
                            prepend_first_insertion_cost=10,
                            append_first_insertion_cost=5,
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

    def job(self, *args, **kargs):
        with QMutexLocker(self.mutex):
            if hasattr(self, 'last_job'):
                self.last_job.cancel()
            self.last_job = Job(*args, **kargs)
            return self.last_job

    def lit(self, query, upper_bound, finished, *args, **kargs):
        self.worker.do(job=self.job(self, query, upper_bound, finished))


class Job(QObject):

    mutex = QMutex()

    def __init__(self, p, query, upper_bound, finished):
        super(Job, self).__init__()
        self.p = p
        self.query = query
        self.upper_bound = upper_bound
        self.finished = finished
        self.canceled = False

    @Slot(object)
    def _make_model(self, args):
        if not self.canceled:
            with QMutexLocker(self.mutex):
                self.finished(RunnableModel(args))
        self.deleteLater()

    def cancel(self):
        self.canceled = True

    def run(self):
        QTimer.singleShot(200, self.run_later)

    def run_later(self):
        """Use mutex to protect self.d."""
        with QMutexLocker(self.p.mutex):
            for runnable in self.p.d.values():
                if self.canceled:
                    break
                runnable.query.update(self.query.lower())

            def f(runnable):
                """Don't calculate editing distance if job stopped."""
                if self.canceled:
                    return 0
                elif not self.query:
                    return runnable.order
                else:
                    return runnable.query.distance_to(runnable.name.lower())

            tasks = []
            if not self.canceled:
                tasks = sorted(self.p.d.values(), key=f)[:self.upper_bound]

            print('%s %d %s %d' % (tasks[0].name, f(tasks[0]), tasks[1].name, f(tasks[1])))

            QMetaObject.invokeMethod(
                self,
                '_make_model',
                Qt.QueuedConnection,
                Q_ARG(object, tasks)
            )
