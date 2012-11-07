#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Windows related utilities.
"""

import win32gui
import win32con
import win32api
import win32process
from win32gui import *
#from win32con import SW_RESTORE, SW_SHOWMINIMIZED, SW_SHOW
from win32con import *
from win32api import (
    GetCurrentThreadId
)
from win32process import (
    AttachThreadInput
)
from ctypes import *
import ctypes
import ctypes.wintypes
from ctypes import (
    POINTER,
    Structure
)
from ctypes.wintypes import (
    DWORD,
    RECT
)


class tagTITLEBARINFO(Structure):
    pass
tagTITLEBARINFO._fields_ = [
    ('cbSize', DWORD),
    ('rcTitleBar', RECT),
    ('rgstate', DWORD * 6),
]
PTITLEBARINFO = POINTER(tagTITLEBARINFO)
LPTITLEBARINFO = POINTER(tagTITLEBARINFO)
TITLEBARINFO = tagTITLEBARINFO


GetWindowThreadProcessId = windll.user32.GetWindowThreadProcessId
AllowSetForegroundWindow = windll.user32.AllowSetForegroundWindow

#win32gui.SystemParametersInfo(
    #win32con.SPI_SETFOREGROUNDLOCKTIMEOUT,
    #0,
    #win32con.SPIF_SENDWININICHANGE | win32con.SPIF_UPDATEINIFILE
#)

def SetForegroundWindowInternal(hWnd):
    if not IsWindow(hWnd):
        return

    # relation time of SetForegroundWindow lock
    lockTimeOut = 0
    hCurrWnd = GetForegroundWindow()
    dwThisTID = GetCurrentThreadId()
    dwCurrTID = GetWindowThreadProcessId(hCurrWnd, 0)

    # we need to bypass some limitations from Microsoft :)
    if dwThisTID != dwCurrTID:
        AttachThreadInput(dwThisTID, dwCurrTID, TRUE)

        SystemParametersInfo(
            SPI_SETFOREGROUNDLOCKTIMEOUT,0,SPIF_SENDWININICHANGE | SPIF_UPDATEINIFILE)

        AllowSetForegroundWindow(ASFW_ANY)

    SetForegroundWindow(hWnd)

    if dwThisTID != dwCurrTID:
        AttachThreadInput(dwThisTID, dwCurrTID, FALSE)


def goto(hwnd):
    if not win32gui.IsWindow(hwnd):
        return

    _, showCmd, _, _, _ = win32gui.GetWindowPlacement(hwnd)

    # to show window owned by admin process when running in user process
    # see http://msdn.microsoft.com/en-us/library/windows/desktop/ms633548(v=vs.85).aspx
    # for details
    if showCmd == SW_SHOWMINIMIZED:
        #win32gui.ShowWindow(hwnd, SW_RESTORE)
        win32api.SendMessage(hwnd, win32con.WM_SYSCOMMAND, win32con.SC_RESTORE, 0)
    else:
        #win32gui.ShowWindow(hwnd, SW_SHOW)
        win32api.SendMessage(hwnd, win32con.WM_SYSCOMMAND, win32con.SW_SHOW, 0)

    fgwin = win32gui.GetForegroundWindow()
    fg = win32process.GetWindowThreadProcessId(fgwin)[0]
    current = win32api.GetCurrentThreadId()
    if current != fg:
        win32process.AttachThreadInput(fg, current, True)
        win32gui.BringWindowToTop(hwnd)
        win32gui.SetForegroundWindow(hwnd)
        win32gui.SetActiveWindow(hwnd)
        #win32gui.SetFocus(hwnd)
        win32process.AttachThreadInput(fg, win32api.GetCurrentThreadId(), False)
    else:
        win32gui.SetForegroundWindow(hwnd)


def gotold(hwnd):
    if not win32gui.IsWindow(hwnd):
        return

    _, showCmd, _, _, _ = win32gui.GetWindowPlacement(hwnd)

    if showCmd == SW_SHOWMINIMIZED:
        win32gui.ShowWindow(hwnd, SW_RESTORE)
    else:
        win32gui.ShowWindow(hwnd, SW_SHOW)

    win32gui.SetForegroundWindow(hwnd)
    win32gui.SetActiveWindow(hwnd)


def is_alt_tab_window(hwnd):
    """Check whether a window is shown in alt-tab.

    See http://stackoverflow.com/a/7292674/238472 for details.
    """
    if not win32gui.IsWindowVisible(hwnd):
        return False

    hwnd_walk = win32con.NULL
    hwnd_try = ctypes.windll.user32.GetAncestor(hwnd, win32con.GA_ROOTOWNER)
    while hwnd_try != hwnd_walk:
        hwnd_walk = hwnd_try
        hwnd_try = ctypes.windll.user32.GetLastActivePopup(hwnd_walk)
        if win32gui.IsWindowVisible(hwnd_try):
            break

    if hwnd_walk != hwnd:
        return False

    # the following removes some task tray programs and "Program Manager"
    ti = TITLEBARINFO()
    ti.cbSize = ctypes.sizeof(ti)
    ctypes.windll.user32.GetTitleBarInfo(hwnd, ctypes.byref(ti))
    if ti.rgstate[0] & win32con.STATE_SYSTEM_INVISIBLE:
        return False

    # Tool windows should not be displayed either, these do not appear in the
    # task bar.
    if win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) & win32con.WS_EX_TOOLWINDOW:
        return False

    return True
