#!/usr/bin/env python
# -*- coding: utf-8 -*-


import uuid
from qt.QtCore import (
    QObject,
    QTimer,
    QTime
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

    def set_done_handle(self, done):
        pass

    @property
    def finished(self):
        _no_impl(self.finished.__name__)

    @property
    def id(self):
        return self._id


class LitPlugin(object):

    def __init__(self):
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
        self.super.__init__()
        self.jobs = deque()
        self.idle_count = 0
        self.timer = QTime()

    @property
    def super(self):
        return super(Worker, self)

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
