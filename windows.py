#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Windows related utilities.
"""

import win32gui
import win32con
import win32api
import win32process
import win32security
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
    LONG,
    WORD,
    BYTE,
    RECT,
    UINT,
    ATOM
)
from pywingui.winuser import MAKEINTRESOURCE

from PyQt4.QtGui import QPixmap, QImage
from PyQt4.QtCore import Qt
import logging
import win32com.client
import logging


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

ASFW_ANY = -1


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


import wmi
c = wmi.WMI()


def get_app_path(hwnd):
    """Get applicatin path given hwnd."""
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        for p in c.query('SELECT ExecutablePath FROM Win32_Process WHERE ProcessId = %s' % str(pid)):
            exe = p.ExecutablePath
            break
    except:
        return None
    else:
        return exe


def get_app_name(hwnd):
    """Get applicatin filename given hwnd."""
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        for p in c.query('SELECT Name FROM Win32_Process WHERE ProcessId = %s' % str(pid)):
            exe = p.Name
            break
    except:
        return None
    else:
        return exe


def AdjustPrivilege(priv, enable = 1):
    # Get the process token.
    flags = win32con.TOKEN_ADJUST_PRIVILEGES | win32con.TOKEN_QUERY
    htoken = win32security.OpenProcessToken(win32api.GetCurrentProcess(), flags)
    # Get the ID for the system shutdown privilege.
    id = win32security.LookupPrivilegeValue(None, priv)
    # Now obtain the privilege for this process.
    # Create a list of the privileges to be added.
    if enable:
        newPrivileges = [(id, win32con.SE_PRIVILEGE_ENABLED)]
    else:
        newPrivileges = [(id, 0)]
    # and make the adjustment.
    win32security.AdjustTokenPrivileges(htoken, 0, newPrivileges)


def elevate():
    import os
    import win32security

    pid = os.getpid()
    phandle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, False, pid)
    token_handle=win32security.OpenProcessToken(phandle,win32con.TOKEN_ALL_ACCESS)
    if token_handle==0:
        print('提取令牌失败')
    else:
        Luid=win32security.LookupPrivilegeValue(None,win32security.SE_DEBUG_NAME)
        if Luid==0:
            print('Luid获取失败')
        else:
            new_token_pricileges=[(Luid,win32security.SE_PRIVILEGE_ENABLED)]
            i=win32security.AdjustTokenPrivileges(token_handle,0,new_token_pricileges)
            if i==0:
                print('提权失败')
            else:
                print('succ')
    win32api.CloseHandle(token_handle)


def goto(hwnd):
    #_, pid = win32process.GetWindowThreadProcessId(hwnd)
    #shell = win32com.client.Dispatch('WScript.Shell')
    #shell.AppActivate(pid)
    #shell.SendKeys(r'(% )x')
    #_old(hwnd)
    _goto_autoit(hwnd)


def close_window(hwnd):
    win32gui.SendMessage(hwnd, win32con.WM_CLOSE, None, None);
    #win32gui.CloseWindow(hwnd)


autoit = None


def _register_autoit():
    import subprocess as sp
    sp.call(['regsvr32.exe', '/s', 'AutoItX3.dll'])


def _init_autoit():
    global autoit
    if not autoit:
        make = lambda: win32com.client.Dispatch('AutoItX3.Control')
        try:
            autoit = make()
        except:
            try:
                _register_autoit()
                autoit = make()
            except Exception as e:
                logging.error('Autoit initialization failed.')
                logging.exception(e)
                return
        logging.debug('Autoit intialized.')


def _goto_autoit(hwnd):
    _init_autoit()
    # prevent ambigularity
    # remove 0x prefix
    autoit.WinActivate('[HANDLE:%s]' % hex(hwnd)[2:])


def _old(hwnd):
    """So ugly here..."""
    if not win32gui.IsWindow(hwnd):
        return


    fgwin = win32gui.GetForegroundWindow()
    fg, fp = win32process.GetWindowThreadProcessId(fgwin)
    current = win32api.GetCurrentThreadId()

    try:
        attached = False
        if current != fg and fg:
            try:
                attached = win32process.AttachThreadInput(fg, current, True)
            except:
                pass
            #AllowSetForegroundWindow(ASFW_ANY)
        _, showCmd, _, _, _ = win32gui.GetWindowPlacement(hwnd)
        # to show window owned by admin process when running in user process
        # see http://msdn.microsoft.com/en-us/library/windows/desktop/ms633548(v=vs.85).aspx
        # for details
        if showCmd == win32con.SW_SHOWMINIMIZED:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            #win32api.SendMessage(hwnd, win32con.WM_SYSCOMMAND, win32con.SC_RESTORE, 0)
        else:
            win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
            #win32api.SendMessage(hwnd, win32con.WM_SYSCOMMAND, win32con.SW_SHOW, 0)

        for fn in [
            win32gui.BringWindowToTop,
            win32gui.SetForegroundWindow,
            win32gui.SetActiveWindow,
            win32gui.SetFocus
        ]:
            try:
                fn(hwnd)
            except Exception as e:
                logging.error(str(e))
    except Exception as e:
        logging.error(str(e))
    finally:
        if attached:
            win32process.AttachThreadInput(fg, win32api.GetCurrentThreadId(), False)
        #else:
            #win32gui.SetForegroundWindow(hwnd)


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
    if not win32gui.IsWindowVisible(hwnd) or not win32gui.IsWindow(hwnd):
        return False

    if not window_title(hwnd):
        return False

    #hwnd_walk = win32con.NULL
    #hwnd_try = ctypes.windll.user32.GetAncestor(hwnd, win32con.GA_ROOTOWNER)
    #while hwnd_try != hwnd_walk:
        #hwnd_walk = hwnd_try
        #hwnd_try = ctypes.windll.user32.GetLastActivePopup(hwnd_walk)
        #if win32gui.IsWindowVisible(hwnd_try):
            #break

    #if hwnd_walk != hwnd:
        #return False

    # the following removes some task tray programs and "Program Manager"
    # but QQ and Thunder won't show either
    #ti = TITLEBARINFO()
    #ti.cbSize = ctypes.sizeof(ti)
    #ctypes.windll.user32.GetTitleBarInfo(hwnd, ctypes.byref(ti))
    #if ti.rgstate[0] & win32con.STATE_SYSTEM_INVISIBLE:
        #return False

    # Tool windows should not be displayed either, these do not appear in the
    # task bar.
    if win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) & win32con.WS_EX_TOOLWINDOW:
        return False

    pwi = WINDOWINFO()
    windll.user32.GetWindowInfo(hwnd, byref(pwi))
    # A top-level window created with this style does not become the foreground
    # window when the user clicks it. The system does not bring this window to
    # the foreground when the user minimizes or closes the foreground window.
    # The window does not appear on the taskbar by default.
    if pwi.dwExStyle & win32con.WS_EX_NOACTIVATE:
        return False

    return True


def window_title(hwnd):
    return win32gui.GetWindowText(hwnd)


def get_hicon(hWin):
    hIcon = win32api.SendMessage(hWin, win32con.WM_GETICON, win32con.FALSE, 0)
    if hIcon == win32con.NULL:
        hIcon = win32api.SendMessage(hWin, win32con.WM_GETICON, win32con.TRUE, 0)
    if hIcon == win32con.NULL:
        hIcon = win32gui.GetClassLong(hWin, win32con.GCL_HICONSM)
    if hIcon == win32con.NULL:
        hIcon = win32gui.GetClassLong(hWin, win32con.GCL_HICON)
    if hIcon == win32con.NULL:
        hIcon = win32gui.LoadIcon(win32con.NULL, MAKEINTRESOURCE(win32con.IDI_APPLICATION))
    return hIcon


def valid_handle(h):
    return h != win32con.NULL


def make_qicon(hicon):
    width = 16
    height = 16
    if valid_handle(hicon):
        return QPixmap.fromWinHICON(hicon).scaled(width, height)
    else:
        ret = QPixmap(width, height)
        ret.fill(Qt.transparent)
        return ret


#def get_file_icon(path):
    #i = win32gui.ExtractIconEx(path, 0)[0]
    ##return win32gui.LoadIcon(i, 0)
    #return i


from geticon import get_file_icon


def get_window_icon(hwnd):
    """Return QPixmap."""
    #hicon = win32gui.GetClassLong(hwnd, win32con.GCL_HICON)
    hicon = get_hicon(hwnd)
    if not valid_handle(hicon):
        return None
    try:
        return make_qicon(hicon)
    except:
        return None
    #info = win32gui.GetIconInfo(hicon)
    #try:
        #return QPixmap.fromWinHBITMAP(info[4])
    #finally:
        #for i in [3, 4]:
            #info[i].close()


class tagBITMAPINFOHEADER(Structure):
    pass
tagBITMAPINFOHEADER._fields_ = [
    ('biSize', DWORD),
    ('biWidth', LONG),
    ('biHeight', LONG),
    ('biPlanes', WORD),
    ('biBitCount', WORD),
    ('biCompression', DWORD),
    ('biSizeImage', DWORD),
    ('biXPelsPerMeter', LONG),
    ('biYPelsPerMeter', LONG),
    ('biClrUsed', DWORD),
    ('biClrImportant', DWORD),
]
PBITMAPINFOHEADER = POINTER(tagBITMAPINFOHEADER)
BITMAPINFOHEADER = tagBITMAPINFOHEADER
LPBITMAPINFOHEADER = POINTER(tagBITMAPINFOHEADER)


class tagRGBQUAD(Structure):
    pass
tagRGBQUAD._fields_ = [
    ('rgbBlue', BYTE),
    ('rgbGreen', BYTE),
    ('rgbRed', BYTE),
    ('rgbReserved', BYTE),
]
RGBQUAD = tagRGBQUAD
LPRGBQUAD = POINTER(RGBQUAD)


class tagBITMAPINFO(Structure):
    pass
tagBITMAPINFO._fields_ = [
    ('bmiHeader', BITMAPINFOHEADER),
    ('bmiColors', RGBQUAD * 1),
]
PBITMAPINFO = POINTER(tagBITMAPINFO)
LPBITMAPINFO = POINTER(tagBITMAPINFO)
BITMAPINFO = tagBITMAPINFO


def qt_fromWinHBITMAP(hdc, bitmap, w, h):
    bmi = BITMAPINFO()
    ctypes.memset(ctypes.byref(bmi), 0, ctypes.sizeof(bmi))
    bmi.bmiHeader.biSize        = ctypes.sizeof(BITMAPINFOHEADER)
    bmi.bmiHeader.biWidth       = w
    bmi.bmiHeader.biHeight      = -h
    bmi.bmiHeader.biPlanes      = 1
    bmi.bmiHeader.biBitCount    = 32
    bmi.bmiHeader.biCompression = win32con.BI_RGB
    bmi.bmiHeader.biSizeImage   = w * h * 4

    image = QImage(w, h, QImage.Format_ARGB32_Premultiplied)
    if image.isNull():
        return image

    # Get bitmap bits
    data = ctypes.create_string_buffer(bmi.bmiHeader.biSizeImage)

    if ctypes.windll.gdi32.GetDIBits(
        hdc,
        bitmap,
        0,
        h,
        data,
        ctypes.byref(bmi),
        win32con.DIB_RGB_COLORS
    ):
        # Create image and copy data into image.
        for y in range(h):
            dest = image.scanLine(y);
            offset = y * image.bytesPerLine()
            dest[:] = data.raw[offset:offset + image.bytesPerLine()]
    else:
        logging.error("qt_fromWinHBITMAP(), failed to get bitmap bits")

    return image

#def fromWinHICON(icon):
    #foundAlpha = False
    #screenDevice = win32gui.GetDC(0)
    #hdc = win32gui.CreateCompatibleDC(screenDevice)
    #win32gui.ReleaseDC(0, screenDevice)

    #fIcon, xHotspot, yHotspot, hbmMask, hbmColor = win32gui.GetIconInfo(icon)  # x and y Hotspot describes the icon center

    #w = xHotspot * 2;
    #h = yHotspot * 2;

    #bitmapInfo = BITMAPINFOHEADER()
    #bitmapInfo.biSize        = ctypes.sizeof(BITMAPINFOHEADER)
    #bitmapInfo.biWidth       = w
    #bitmapInfo.biHeight      = h
    #bitmapInfo.biPlanes      = 1
    #bitmapInfo.biBitCount    = 32
    #bitmapInfo.biCompression = win32con.BI_RGB
    #bitmapInfo.biSizeImage   = 0
    #bitmapInfo.biXPelsPerMeter = 0
    #bitmapInfo.biYPelsPerMeter = 0
    #bitmapInfo.biClrUsed       = 0
    #bitmapInfo.biClrImportant  = 0

    #winBitmap = ctypes.windll.gdi32.CreateDIBSection(
        #hdc,
        #ctypes.byref(bitmapInfo),
        #win32con.DIB_RGB_COLORS,
        #ctypes.c_void_p(),
        #win32con.NULL,
        #0
    #)
    #oldhdc = win32gui.SelectObject(hdc, winBitmap)
    #win32gui.DrawIconEx(hdc, 0, 0, icon, xHotspot * 2,
                        #yHotspot * 2, 0, 0, DI_NORMAL)
    #image = qt_fromWinHBITMAP(hdc, winBitmap, w, h)

    ##for y in range(h):
        ##if foundAlpha:
            ##break
        ##QRgb *scanLine= reinterpret_cast<QRgb *>(image.scanLine(y));
        ##for (int x = 0; x < w ; x++) {
            ##if (qAlpha(scanLine[x]) != 0) {
                ##foundAlpha = true;
                ##break;
            ##}
        ##}
    ##}
    ##if not foundAlpha):
        ### If no alpha was found, we use the mask to set alpha values
        ##win32gui.DrawIconEx(hdc, 0, 0, icon, w, h, 0, 0, win32con.DI_MASK)
        ##mask = qt_fromWinHBITMAP(hdc, winBitmap, w, h)

        ##for y in range(h):
            ##QRgb *scanlineImage = reinterpret_cast<QRgb *>(image.scanLine(y));
            ##QRgb *scanlineMask = mask.isNull() ? 0 : reinterpret_cast<QRgb *>(mask.scanLine(y));
            ##for (int x = 0; x < w ; x++){
                ##if (scanlineMask && qRed(scanlineMask[x]) != 0)
                    ##scanlineImage[x] = 0; //mask out this pixel
                ##else
                    ##scanlineImage[x] |= 0xff000000; // set the alpha channel to 255

    ## dispose resources created by iconinfo call
    #win32gui.DeleteObject(hbmMask)
    #win32gui.DeleteObject(hbmColor)

    #win32gui.SelectObject(hdc, oldhdc)  # restore state
    #win32gui.DeleteObject(winBitmap)
    #win32gui.DeleteDC(hdc)
    #return QPixmap.fromImage(image)


class tagWINDOWINFO(Structure):

    def __str__(self):
        return '\n'.join([key + ':' + str(getattr(self, key)) for key, value in self._fields_])

tagWINDOWINFO._fields_ = [
    ('cbSize', DWORD),
    ('rcWindow', RECT),
    ('rcClient', RECT),
    ('dwStyle', DWORD),
    ('dwExStyle', DWORD),
    ('dwWindowStatus', DWORD),
    ('cxWindowBorders', UINT),
    ('cyWindowBorders', UINT),
    ('atomWindowType', ATOM),
    ('wCreatorVersion', WORD),
]
WINDOWINFO = tagWINDOWINFO
LPWINDOWINFO = POINTER(tagWINDOWINFO)
PWINDOWINFO = POINTER(tagWINDOWINFO)


def top_level_windows():
    """ Returns the top level windows in a list of hwnds."""
    windows = []
    win32gui.EnumWindows(_window_enum_top_level, windows)
    return windows


def window_title(hwnd):
    return win32gui.GetWindowText(hwnd)


def _window_enum_top_level(hwnd, windows):
    """ Window Enum function for getTopLevelWindows """
    #if win32gui.GetParent(hwnd) == 0 and title != '':
    if is_alt_tab_window(hwnd):
        windows.append(hwnd)
