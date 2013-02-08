#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from files import Files


class Run(Files):

    def __init__(self, worker):
        super(Run, self).__init__(worker)
        self._paths = []
        for path in os.environ['PATH'].split(os.pathsep):
            path = os.path.expandvars(path)
            if os.path.exists(path):
                for filename in os.listdir(path):
                    _, ext = os.path.splitext(filename)
                    if ext in ['.exe', '.cmd', '.bat', '.lnk']:
                        self._paths.append(os.path.join(path, filename))
        self.path_list_changed()

    @property
    def paths(self):
        return self._paths

    @property
    def name(self):
        return 'r'
