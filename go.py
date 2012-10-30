#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lit import LitPlugin
import re
import win32gui
from win32con import SW_RESTORE, SW_SHOWMINIMIZED, SW_SHOW
import windows
from datetime import datetime


class Go(LitPlugin):

    def __init__(self):
        self.select_count = dict()

    @property
    def name(self):
        return 'g'

    def lit(self, query):
        self.windows = self._getTopLevelWindows()
        words = [re.escape(w) for w in query]
        query = '.*'.join(words)
        pattern = re.compile(query, flags=re.IGNORECASE)
        windownames = [w[1] for w in self.windows if not pattern.search(w[1]) is None]
        for name in windownames:
            if not name in self.select_count:
                self.select_count[name] = datetime.now()
        return sorted(windownames, key=lambda name: self.select_count[name], reverse=True)
        # Icon for the window can be extracted with WM_GETICON, but it's too much for now

    def select(self, arg):
        for window in self.windows:
            if arg == window[1]:
                self.select_count[arg] = datetime.now()
                windows.goto(window[0])
                return
        del self.select_count[arg]

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
