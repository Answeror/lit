#!/usr/bin/env python
# -*- coding: utf-8 -*-


import uuid
from qt.QtCore import (
    QObject,
    QTimer,
    QTime,
    Signal,
    QThread
)
from collections import deque


def _no_impl(name):
    raise RuntimeError('Method %s not implemented.' % name)


class LitJob(object):
    """Time comsuming job base class."""

    def __init__(self):
        # use random uuid generator
        # see <http://goo.gl/JHrfc> for reason
        self._id = uuid.uuid4()

    def stop(self):
        pass

    def __call__(self):
        pass

    @property
    def main(self):
        """Whether need to be run in main (GUI) thread."""
        return False

    @property
    def id(self):
        return self._id


class LitPlugin(object):

    def __init__(self):
        pass

    def setup(self):
        pass

    def teardown(self):
        pass

    def lit(self, query):
        return []

    def act(self):
        pass

    def select(self, arg):
        pass

    @property
    def name(self):
        _no_impl(self.name.__name__)


class Worker(QObject):

    def __init__(self):
        QObject.__init__(self)
        self.jobs = deque()
        self.idle_count = 0
        self.timer = QTime()

    def do(self, job):
        self.jobs.append(job)

    def run(self):
        self.timer.restart()
        if self.jobs:
            job = self.jobs.popleft()
            job()
            self.idle_count = 0
        else:
            self.idle_count += 1

        # to avoid high CPU
        if self.idle_count < 1:
            # TODO: maybe check CPU here?
            QTimer.singleShot(self.timer.elapsed(), self.run)
        else:
            QTimer.singleShot(100, self.run)


class AsyncStoppableJob(QThread):

    done = Signal(object)

    def __init__(self, job):
        QThread.__init__(self)
        self.job = job

    def __call__(self):
        self.start()

    def run(self):
        ret = self.job()
        # do not call done if job been stpped
        # to prevent popup flicker
        if not self.job.stopped:
            self.done.emit(ret)

    def stop(self):
        self.job.stop()

    @property
    def finished(self):
        return self.isFinished()
