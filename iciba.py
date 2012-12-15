#!/usr/bin/env python
# -*- coding: utf-8 -*-


from urllib.parse import urlencode
import urllib3
from common import LitPlugin, LitJob
import logging
import webbrowser


BASE = 'http://www.iciba.com/index.php'


def _uri(key):
    return '%s?%s' % (BASE, urlencode({'a': 'suggest', 's': key.replace(' ', '|1{')}))


def _trans_uri(query):
    return 'http://cdict.net/?%s' % urlencode({'q': query})


def _parse(data):
    def inner():
        for line in data.decode('utf-8').split('\n'):
            key = line.strip().split('_')[0].replace('|1{', ' ')
            if key:
                yield key
    return list(inner())


class Iciba(LitPlugin):

    def __init__(self):
        super(Iciba, self).__init__()
        self.http = urllib3.PoolManager()

    @property
    def name(self):
        return 't'

    def _fetch(self, key):
        r = self.http.request('GET', _uri(key))
        if r.status == 200:
            return r.data
        else:
            return None

    def _query(self, key):
        try:
            data = self._fetch(key)
            if data:
                return _parse(data)
        except Exception as e:
            logging.error(e)
            return None

    def lit(self, query, *args, **kargs):
        return Job(self, query)

    def select(self, content, index):
        try:
            webbrowser.open(_trans_uri(content[index.row()]))
        except Exception as e:
            logging.error(e)


class Job(LitJob):

    def __init__(self, master, query):
        super(Job, self).__init__()
        self.master = master
        self.query = query
        self._finished = False

    @property
    def finished(self):
        return self._finished

    def __call__(self):
        result = self.master._query(self.query)
        self._finished = not result is None
        return result
