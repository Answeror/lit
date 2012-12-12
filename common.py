#!/usr/bin/env python
# -*- coding: utf-8 -*-


import uuid


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
