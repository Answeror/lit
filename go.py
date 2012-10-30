#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lit import LitPlugin
import re
import win32gui
from win32con import SW_RESTORE, SW_SHOWMINIMIZED, SW_SHOW
import windows
from datetime import datetime
from utils import damerau_levenshtein_distance


class Go(LitPlugin):

    def __init__(self):
        self.usetime = dict()

    @property
    def name(self):
        return 'g'

    def lit(self, query):
        self.windows = self._getTopLevelWindows()
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
        return sorted(names, key=f)
        # Icon for the window can be extracted with WM_GETICON, but it's too much for now

    def select(self, arg):
        for window in self.windows:
            if arg == window[1]:
                self.usetime[arg] = datetime.now()
                windows.goto(window[0])
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
        if win32gui.GetParent(hwnd) == 0 and title != '':
            windowsList.append((hwnd, title))
