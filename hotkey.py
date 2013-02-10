#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ctypes
from ctypes import CFUNCTYPE, c_int, POINTER, c_void_p, windll
from hook import KeyboardHook
import win32con
import timer


##################################################
# returns a function pointer to the fn paramater #
# assumes the function takes three params:       #
# c_int, c_int, and POINTER(c_void_p)            #
##################################################
def getFunctionPointer(fn):
    CMPFUNC = CFUNCTYPE(c_int, c_int, c_int, POINTER(c_void_p))
    return CMPFUNC(fn)


modifiers = [
    ('control', 1 << 1, 0x11),
    ('win', 1 << 3, 0x5b),
    ('alt', 1 << 0, 0x12),
    ('shift', 1 << 2, 0x10)
]


def mods():
    windll.user32.GetKeyState(0)  # flush
    keyState = (ctypes.c_uint8 * 256)()  # Array of c_long
    windll.user32.GetKeyboardState(ctypes.byref(keyState))
    ms = []
    for mod in modifiers:
        if keyState[mod[2]] & 1 << 7:
            ms.append(mod[0])
        keyState[mod[2]] = 0
    return ms


class Hotkey(object):

    def __init__(self, fire):
        self.fire = fire
        self.presscount = 0
        self.delay = 300
        self.timer_id = None

        import win32com.client
        self.shell = win32com.client.Dispatch("WScript.Shell")

        self.keyboardHook = KeyboardHook()
        self.pending = False

    def go(self):
        if self.timer_id is not None:
            timer.kill_timer(self.timer_id)
            self.timer_id = None
        if self.presscount >= 2:
            self.presscount = 0
            self.fire()
        else:
            x = self.presscount
            if x > 0:
                self.presscount = 0
                self.pending = True
                try:
                    self.shell.SendKeys(';' * x)
                finally:
                    self.pending = False

    def timer_fn(self, id, time):
        self.go()

    def kbEvent(self, nCode, wParam, lParam):
        if nCode >= 0:
            # It just occured to me that I should aso be checking for WM_SYSKEYDOWN as well
            if wParam is win32con.WM_KEYDOWN:
                if not self.pending and lParam[0] == 0xBA and not mods():
                    if self.presscount >= 0:
                        if self.timer_id is None:
                            self.timer_id = timer.set_timer(self.delay, self.timer_fn)
                    self.presscount += 1
                    if self.presscount > 0:
                        # return a non-zero to prevent further processing
                        return 42
                else:
                    self.go()
        return windll.user32.CallNextHookEx(self.keyboardHook.kbHook, nCode, wParam, lParam)

    def start(self):
        pointer = getFunctionPointer(self.kbEvent)
        if not self.keyboardHook.installHook(pointer):
            raise RuntimeError('Install keyboard hook failed.')
        self.keyboardHook.keepAlive()

    def stop(self):
        self.keyboardHook.stop()
