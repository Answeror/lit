from qt.QtGui import (
    QPixmap,
    QIcon
)

from win32com.shell import shell, shellcon
import win32con

import win32gui
import pywintypes
import os


def extract_file_icon(path):
    largeicons, smallicons = win32gui.ExtractIconEx(path, 0)
    fIcon, xHotspot, yHotspot, hbmMask, hbmColor = win32gui.GetIconInfo(largeicons[0])
    pixmap = QPixmap.fromWinHBITMAP(hbmColor, QPixmap.PremultipliedAlpha)
    icon = QIcon(pixmap)
    hbmColor.close()
    hbmMask.close()
    for hIcon in largeicons + smallicons:
        win32gui.DestroyIcon(hIcon)
    return icon


def splitparts(path):
    rv = []
    while path:
        path, tail = os.path.split(path)
        if not tail:
            break
        rv.append(tail)
    return rv[::-1]


def translate_path(path):
    if path.lower().startswith('\\systemroot\\'):
        parts = splitparts(path)
        parts[0] = os.environ['SystemRoot']
        path = os.path.join(*parts)
    return path


def get_file_icon_by_shell(path):
    path = translate_path(path)
    flags, (hIcon, iIcon, dwAttributes, displayName, typeName) = shell.SHGetFileInfo(
        path,
        0,
        shellcon.SHGFI_ICON|shellcon.SHGFI_SMALLICON|shellcon.SHGFI_SYSICONINDEX|shellcon.SHGFI_TYPENAME|shellcon.SHGFI_USEFILEATTRIBUTES,
    )
    if hIcon == win32con.NULL:
        return None
    pixmap = QPixmap.fromWinHICON(hIcon)
    win32gui.DestroyIcon(hIcon)
    icon = QIcon(pixmap)
    return icon


def get_file_icon(path):
    try:
        return get_file_icon_by_shell(path)
    except pywintypes.error:
        pass
