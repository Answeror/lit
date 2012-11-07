#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lit import LitPlugin
import win32gui
import windows as winutils
from datetime import datetime
from utils import damerau_levenshtein_distance
import stream as sm
from PySide.QtCore import Qt, QAbstractListModel


class WindowModel(QAbstractListModel):

    def __init__(self, names, icons):
        self.super.__init__()
        self.names = names
        self.icons = icons

    @property
    def super(self):
        return super(WindowModel, self)

    def rowCount(self, parent):
        return len(self.names)

    def columnCount(self, parent):
        return 1

    def data(self, index, role):
        if not index.isValid():
            return None
        if role == Qt.TextAlignmentRole:
            return int(Qt.AlignLeft | Qt.AlignVCenter)
        elif role == Qt.DisplayRole:
            return self.names[index.row()]
        elif role == Qt.DecorationRole:
            return self.icons[index.row()]
        else:
            return None


class Go(LitPlugin):

    def __init__(self):
        self.usetime = dict()

    @property
    def name(self):
        return 'g'

    def sorted_window_names(self, query):
        names = [w[1] for w in self.windows]

        # update use time
        for name in names:
            if not name in self.usetime:
                self.usetime[name] = datetime.now()

        # sort by lash use
        if not query:
            return sorted(names, key=lambda name: self.usetime[name], reverse=True)

        query = query.lower()
        f = lambda name: damerau_levenshtein_distance(
            query,
            name.lower(),
            insertion_cost=1,
            deletion_cost=100,
            substitution_cost=100,
            transposition_cost=10
        )
        # Icon for the window can be extracted with WM_GETICON, but it's too much for now
        return sorted(names, key=f)

    def update_window_list(self):
        self.windows = self._getTopLevelWindows()

    def lit(self, query, upper_bound, *args, **kargs):
        self.update_window_list()
        names = self.sorted_window_names(query)[:upper_bound]
        d = dict(self.windows >> sm.apply(lambda h, n: (n, h)))
        hwnds = names >> sm.map(lambda name: d[name]) >> list
        icons = hwnds >> sm.map(winutils.get_window_icon) >> list
        return WindowModel(names, icons)

    def select(self, arg):
        for window in self.windows:
            if arg == window[1]:
                self.usetime[arg] = datetime.now()
                winutils.goto(window[0])
                return
        del self.usetime[arg]

    def _getTopLevelWindows(self):
        """ Returns the top level windows in a list of tuples defined (HWND, title) """
        windows = []
        win32gui.EnumWindows(self._windowEnumTopLevel, windows)
        return windows

    @staticmethod
    def _windowEnumTopLevel(hwnd, windowsList):
        """ Window Enum function for getTopLevelWindows """
        title = win32gui.GetWindowText(hwnd)
        #if win32gui.GetParent(hwnd) == 0 and title != '':
        if winutils.is_alt_tab_window(hwnd):
            windowsList.append((hwnd, title))
