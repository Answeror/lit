#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

    if showCmd == SW_SHOWMINIMIZED:
        win32gui.ShowWindow(hwnd, SW_RESTORE)
    else:
        win32gui.ShowWindow(hwnd, SW_SHOW)

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
