#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from ctypes import *
import win32con, win32api, win32gui

class KeyboardHook(object):
    """
    Written by: TwhK / Kheldar
    What do? Installs a global keyboard hook

    To install the hook, call the (gasp!) installHook() function.
    installHook() takes a pointer to the function that will be called
    after a keyboard event.  installHook() returns True if everything
    was successful, and False if it failed
    Note:  I've also provided a function to return a valid function pointer

    To make sure the hook is actually doing what you want, call the
    keepAlive() function
    Note:  keepAlive() doesn't return until kbHook is None, so it should
    be called from a separate thread

    To uninstall the hook, call uninstallHook()

    Note:  relies on modules provided by pywin32.
    http://sourceforge.net/projects/pywin32/
    """
    def __init__(self):
        self.user32     = windll.user32
        self.kbHook     = None

    def installHook(self, pointer):
        self.kbHook = self.user32.SetWindowsHookExA(
                              win32con.WH_KEYBOARD_LL,
                              pointer,
                              win32api.GetModuleHandle(None),
                              0 # this specifies that the hook is pertinent to all threads
        )
        if not self.kbHook:
            return False
        return True

    def stop(self):
        self.uninstallHook()
        self.kbHook = None

    def keepAlive(self):
        if self.kbHook is None:
            return
        while self.kbHook is not None:
            win32gui.PumpWaitingMessages()
            #time.sleep(0.04)  # 25Hz
            time.sleep(0.001) # prevent delay when hold press

    def uninstallHook(self):
        if self.kbHook is None:
            return
        self.user32.UnhookWindowsHookEx(self.kbHook)
        self.kbHook = None
