#!/usr/bin/env python
# -*- coding: utf-8 -*-

from files import Files
from win32com.shell import shell, shellcon
import os
from fs.osfs import OSFS


class Recent(Files):

    def __init__(self):
        super(Recent, self).__init__()
        self._paths = []
        # http://python.6.n6.nabble.com/Access-Most-Recently-Used-MRU-entries-td1953541.html
        self.mru_path = shell.SHGetSpecialFolderPath(0, shellcon.CSIDL_RECENT, 0)
        self.mrufs = OSFS(self.mru_path)
        self.watcher = None

    def setup(self):
        self._update_path()
        self.watcher = self.mrufs.add_watcher(lambda e: self._update_path())

    def _update_path(self):
        self._paths = [os.path.join(self.mru_path, f) for f in self.mrufs.listdir()]
        self.path_list_changed()

    def teardown(self):
        if self.watcher:
            self.mrufs.del_watcher(self.watcher)

    @property
    def paths(self):
        return self._paths

    @property
    def name(self):
        return 're'

    def lit(self, *args, **kargs):
        return super(Recent, self).lit(*args, **kargs)
