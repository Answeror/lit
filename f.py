#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from common import LitPlugin, LitJob, Worker
from utils import TreeQuery
import win32api
from qt.QtGui import (
    QFileIconProvider,
    QIcon
)
from qt.QtCore import (
    Qt,
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
from collections import defaultdict
import stream as sm


icon_provider = QFileIconProvider()

ROOT = r'E:\doc'


def _file_icon(path):
    return icon_provider.icon(QFileInfo(path))


class Runnable(QObject):

    icon_loaded = Signal()

    def __init__(self, query, worker):
        super(Runnable, self).__init__()
        self.query = query
        self.worker = worker
        self._icon = None

    @property
    def icon(self):
        if self._icon is None:
            #self.worker.do(self._fill_icon)
            self._icon = QIcon(':/unknown.png')
        return self._icon

    @property
    def name(self):
        return self.path

    @property
    def path(self):
        return os.path.join(ROOT, os.sep.join(self.query.path))

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


class F(LitPlugin):

    def __init__(self):
        super(F, self).__init__()
        self.worker = Worker()
        self.mutex = QMutex()
        self.worker.run()

        def tree():
            return defaultdict(tree)

        rootnode = tree()
        rootpath = ROOT
        for basepath, dirnames, filenames in os.walk(rootpath):
            relpath = os.path.relpath(basepath, rootpath)
            parent = rootnode
            if relpath != '.':
                for name in relpath.split(os.sep):
                    parent = parent[name]
            for name in dirnames >> sm.append(filenames):
                parent[name]

        self.tree = TreeQuery(
            tree=rootnode,
            query='',
            insertion_cost=1,
            deletion_cost=100,
            substitution_cost=100,
            transposition_cost=10
        )

    @property
    def name(self):
        return 'f'

    @property
    def paths(self):
        assert False, 'Not implemented.'

    def lit(self, query, upper_bound, *args, **kargs):
        return Job(self, query, upper_bound)

    def select(self, content, index):
        # check content type
        if not isinstance(content, RunnableModel):
            logging.info('wrong content type {}'.format(type(content)))
            return

        name = content.data(index, RunnableModel.NAME_ROLE)
        try:
            win32api.ShellExecute(0, 'open', name, '', '', 1)
        except Exception as e:
            logging.error(e)


class Job(LitJob):

    def __init__(self, master, query, upper_bound):
        LitJob.__init__(self)
        self.done = None
        self.stopped = False
        self.master = master
        self.query = query
        self.upper_bound = upper_bound
        self._finished = False

    def stop(self):
        self.stopped = True

    @property
    def finished(self):
        return self._finished

    def __call__(self):
        """Use mutex to protect self.d."""
        try:
            with QMutexLocker(self.master.mutex):
                for node in self.master.tree.nodes:
                    if not self.stopped:
                        node.update(self.master.tree.query, self.query)
                        self.master.tree.query = self.query

                nodes = sorted(self.master.tree.nodes, key=lambda node: node())\
                        >> sm.map(lambda node: Runnable(node, self.master.worker))\
                        >> sm.item[:self.upper_bound]
                model = RunnableModel(nodes)
                self._finished = not self.stopped
                return None if self.stopped else model
        except Exception as e:
            print(e)
