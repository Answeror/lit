#!/usr/bin/env python
# -*- coding: utf-8 -*-

import win32gui
from win32con import SW_RESTORE, SW_SHOWMINIMIZED, SW_SHOW


def goto(hwnd):
    if not win32gui.IsWindow(hwnd):
        return

    _, showCmd, _, _, _ = win32gui.GetWindowPlacement(hwnd)

    if showCmd == SW_SHOWMINIMIZED:
        win32gui.ShowWindow(hwnd, SW_RESTORE)
    else:
        win32gui.ShowWindow(hwnd, SW_SHOW)

    win32gui.SetForegroundWindow(hwnd)
    win32gui.SetActiveWindow(hwnd)
