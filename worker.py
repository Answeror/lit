#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import deque
from qt.QtCore import (
    Qt,
    QMetaObject,
    QRunnable,
    QThreadPool,
    QThread,
    QObject,
    Signal,
    Slot
)


class Job(QObject):

    finished = Signal(object)

    def __init__(self, impl):
        super(Job, self).__init__()
        self.impl = impl

    @Slot()
    def run(self):
        self.finished.emit(self.impl())
        self.deleteLater()


class Worker(QObject):

    def __init__(self):
        super(Worker, self).__init__()
        self.mainq = deque()
        self.q = deque()
        self.thread = QThread()
        self.thread.start()
        self.root = QObject()
        self.root.moveToThread(self.thread)

    @Slot()
    def deal_main(self):
        """This method must be called in main thread."""
        if self.mainq:
            job = self.mainq.popleft()
            job()
            if self.mainq:
                self.delay_deal_main()

    def delay_call(self, name):
        QMetaObject.invokeMethod(
            self,
            name,
            Qt.QueuedConnection
        )

    def delay_deal_main(self):
        self.delay_call('deal_main')

    @Slot()
    def deal(self):
        if self.q:
            job = self.q.popleft()
            #QThreadPool.globalInstance().start(Runnable(job))
            job.moveToThread(self.thread)
            job.setParent(self.root)
            QMetaObject.invokeMethod(
                job,
                'run',
                Qt.QueuedConnection
            )
            if self.q:
                self.delay_deal()

    def delay_deal(self):
        self.delay_call('deal')

    def do(self, job, finished=None, main=False):
        """Do some asyne job, maybe in main thread."""
        if main:
            self.mainq.append(lambda: finished(job()))
            self.delay_deal_main()
        else:
            job = Job(job)
            if finished:
                job.finished.connect(finished, Qt.QueuedConnection)
            self.q.append(job)
            self.delay_deal()
