#!/usr/bin/env python
# -*- coding: utf-8 -*-


from PySide.QtGui import (
    QApplication,
    QWidget,
    QLineEdit,
    QVBoxLayout,
    QCompleter,
    QStringListModel,
    QKeyEvent,
    QAbstractItemView,
    QListView,
    QItemSelectionModel
)
from PySide.QtCore import (
    Qt,
    QEvent,
    QTimer,
    QThread,
    Signal
)
import stream as sm
import os
import re
import win32gui
import ctypes
import windows
import logging
import win32con


# these config should be saved
MAX_LIST_LENGTH = 12


def winid(self):
    _QWidget_winId = QWidget.winId
    if sys.version_info[0] == 2:
        ctypes.pythonapi.PyCObject_AsVoidPtr.restype = ctypes.c_void_p
        ctypes.pythonapi.PyCObject_AsVoidPtr.argtypes = [ctypes.py_object]
        return ctypes.pythonapi.PyCObject_AsVoidPtr(_QWidget_winId(self))
    elif sys.version_info[0] == 3:
        ctypes.pythonapi.PyCapsule_GetPointer.restype = ctypes.c_void_p
        ctypes.pythonapi.PyCapsule_GetPointer.argtypes = [ctypes.py_object]
        return ctypes.pythonapi.PyCapsule_GetPointer(_QWidget_winId(self), None)


def hwnd(win):
    # Convert PyCObject to a void pointer
    return winid(win)


def _no_impl(name):
    raise RuntimeError('Method %s not implemented.' % name)


class LitPlugin(object):

    def __init__(self):
        pass

    def lit(self, query):
        return []

    def act(self):
        pass

    def select(self, arg):
        pass

    @property
    def name(self):
        _no_impl(self.name.__name__)


class Foo(LitPlugin):

    @property
    def name(self):
        return 'foo'

    def lit(self, query):
        return query


def parse_query(text):
    if not text.startswith('\\'):
        return None, text
    m = re.search(r'\\(\S*)( (.*)){0,1}', text)
    return m.group(1), m.group(2)[1:] if not m.group(2) is None else None


class Lit(QWidget):

    def __init__(self, plugins=[]):
        super(Lit, self).__init__()
        lay = QVBoxLayout()
        self.inp = Input(self.act, self)
        self.inp.textChanged.connect(self.query)
        self.completer = Completer(self.inp)
        #self.inp.setCompleter(self.completer)
        self.completer.activated.connect(self.select)
        lay.addWidget(self.inp)
        self.setLayout(lay)
        self._install_plugins(plugins)
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.Popup
            | Qt.WindowStaysOnTopHint
        )
        self.setWindowTitle('lit')

        self.hotkey_thread = HotkeyThread()
        self.hotkey_thread.fire.connect(self.handle_hotkey)
        self.hotkey_thread.start()

        #sema = Semaphore(0)
        #self.sema = sema
        #self.event_listener = EventListener(sema)
        #self.event_listener.start()
        #self.event_processor = EventProcessor(sema)
        #self.event_processor.fire.connect(self.toggle_visibility)
        #self.event_processor.start()

        #qApp.installEventFilter(self)

        #ctypes.windll.user32.SetWinEventHook(
            #win32con.EVENT_SYSTEM_FOREGROUND,
            #win32con.EVENT_SYSTEM_FOREGROUND ,
            #0,
            #self.WinEventProcCallback, 0, 0,
            #win32con.WINEVENT_OUTOFCONTEXT | win32con.WINEVENT_SKIPOWNPROCESS);

    #def WinEventProcCallback(self, hWinEventHook, dwEvent, hwnd, idObject, idChild, dwEventThread, dwmsEventTime):
        #print('aaa')

    @property
    def super(self):
        return super(Lit, self)

    def _move_to_center(self):
        desktop = QApplication.desktop()
        self.move(
            (desktop.width() - self.width()) // 2,
            (desktop.height() - self.height()) // 2
        )

    def resizeEvent(self, e):
        self._move_to_center()
        self.super.resizeEvent(e)

    def handle_hotkey(self, key):
        self.toggle_visibility()

    def toggle_visibility(self):
        logging.info("visible: {}".format(self.window_shown()))
        if self.window_shown():
            self.hide_window()
        else:
            self.show_window()

    def window_shown(self):
        #return self.isVisible() and not (self.windowState() & Qt.WindowMinimized)
        return self.isVisible()

    def hide_window(self):
        #self.inp.setText('')
        #self.completer.popup().hide()
        #self.setWindowState(self.windowState() | Qt.WindowMinimized)
        self.hide()

    def show_window(self):
        self.show()
        #QTimer.singleShot(100, lambda: windows.goto(hwnd(self)))

    def _install_plugins(self, plugins):
        self.plugins = plugins >> sm.map(lambda p: (p.name, p)) >> dict
        self.default_plugin = plugins[0] if self.plugins else None

    def query(self, text):
        cmd, arg = parse_query(text)

        self.cmd = self.default_plugin.name if cmd is None else cmd
        if arg is None:
            self.popup([])
        else:
            if cmd is None:
                if not self.default_plugin is None:
                    self.popup(self.default_plugin.lit(arg))
            else:
                if cmd in self.plugins:
                    self.popup(self.plugins[cmd].lit(arg))

    def select(self, text):
        cmd = self.cmd
        #self.hide_window()
        self.plugins[cmd].select(text)

    def act(self):
        if self.cmd == 'exit':
            #self.event_listener.terminate()
            #if self.event_processor.isRunning():
                #self.event_processor.running = False
                #self.sema.release()
                #self.event_processor.wait()
            self.hotkey_thread.running = False
            self.hotkey_thread.wait()
            QApplication.quit()
        if self.cmd in self.plugins:
            self.plugins[self.cmd].act()

    def popup(self, items):
        self.completer.update(items[:MAX_LIST_LENGTH])

    def showEvent(self, e):
        QTimer.singleShot(0, lambda: windows.goto(hwnd(self)))
        self.inp.setFocus()
        if not self.completer.popuped:
            QTimer.singleShot(0, lambda: self.query(self.inp.text()))
        self.super.showEvent(e)

    def hideEvent(self, e):
        state = self.inp.blockSignals(True)
        try:
            self.inp.setText('')
        finally:
            self.inp.blockSignals(state)
        self.completer.popup().hide()
        self.super.hideEvent(e)

    def closeEvent(self, e):
        logging.info('closing')
        self.super.closeEvent(e)

    # cannot write here, don't know why
    #def closeEvent(self, e):
        #print('terming')
        #self.event_listener.terminate()
        #print('termed')
        #if self.event_processor.isRunning():
            #self.event_processor.running = False
            #self.sema.release()
            #self.event_processor.wait()
            #print('waited')


class CenterListView(QListView):
    """Always scroll to center."""

    def __init__(self, parent=None):
        self.super.__init__(parent=parent)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        #self.setSpacing(2)
        #self.setItemDelegate(QStyledItemDelegate())

    @property
    def super(self):
        return super(CenterListView, self)

    def scrollTo(self, index, _):
        """Always scroll to center."""
        self.super.scrollTo(index, QAbstractItemView.PositionAtCenter)


class Completer(QCompleter):
    """Custom completer for avaiable tasks."""

    def __init__(self, parent=None):
        super(Completer, self).__init__(parent=parent)
        self.windows = []
        self.setPopup(CenterListView())
        self.setMaxVisibleItems(12)
        if not parent is None:
            self.setWidget(parent)

    @property
    def popuped(self):
        return self.popup().isVisible()

    @property
    def super(self):
        return super(Completer, self)

    def update(self, items):
        model = QStringListModel()
        model.setStringList(items >> sm.map(str) >> list)
        self.setModel(model)
        self.setCompletionPrefix('')
        self.complete()
        first_index = self.popup().model().index(0, 0)
        self.popup().selectionModel().setCurrentIndex(
            first_index,
            QItemSelectionModel.Select | QItemSelectionModel.Rows
        )
        self.popup().scrollTo(first_index, QAbstractItemView.PositionAtCenter)

    @property
    def atbottom(self):
        p = self.popup()
        return p.currentIndex().row() + 1 == p.model().rowCount()

    @property
    def attop(self):
        return self.popup().currentIndex().row() == 0

    def eventFilter(self, o, e):
        if e.type() == QEvent.KeyPress:
            if e.key() == Qt.Key_Tab or e.key() == Qt.Key_J and e.modifiers() & Qt.ControlModifier:
                ne = QKeyEvent(
                    QEvent.KeyPress,
                    Qt.Key_Down,
                    e.modifiers(),
                    ''
                )
                QApplication.sendEvent(o, ne)
                return True
            elif e.key() == Qt.Key_Tab or e.key() == Qt.Key_K and e.modifiers() & Qt.ControlModifier:
                ne = QKeyEvent(
                    QEvent.KeyPress,
                    Qt.Key_Up,
                    e.modifiers(),
                    e.text(),
                    e.isAutoRepeat(),
                    e.count()
                )
                QApplication.sendEvent(o, ne)
                return True
            elif e.key() == Qt.Key_Up and self.attop:
                ne = QKeyEvent(
                    QEvent.KeyPress,
                    Qt.Key_End,
                    Qt.ControlModifier
                )
                QApplication.sendEvent(o, ne)
                return True
            elif e.key() == Qt.Key_Down and self.atbottom:
                ne = QKeyEvent(
                    QEvent.KeyPress,
                    Qt.Key_Home,
                    Qt.ControlModifier
                )
                QApplication.sendEvent(o, ne)
                return True
        return self.super.eventFilter(o, e)


class Input(QLineEdit):

    def __init__(self, enter=lambda: None, parent=None):
        super(Input, self).__init__(parent)
        self.enter = enter

    @property
    def super(self):
        return super(Input, self)

    def keyPressEvent(self, e):
        {
            Qt.Key_Escape: lambda: self.setText(''),
            Qt.Key_Return: self.enter
        }.get(e.key(), lambda: None)()
        super(Input, self).keyPressEvent(e)

    #def setCompleter(self, completer):
        #completer.setWidget(self)


class Application(QApplication):

    def __init__(self, argv):
        self.super.__init__(argv)

    @property
    def super(self):
        return super(Application, self)


class HotkeyThread(QThread):
    """http://evenrain.com/pyside-detect-usb-device-plugin-and-remove/"""

    fire = Signal(int)

    def __init__(self):
        QThread.__init__(self)
        self.running = True

    @property
    def super(self):
        return super(HotkeyThread, self)

    def handle_hotkey(self, hwnd, msg, wp, lp):
        logging.info('fire')
        self.fire.emit(int(wp))
        return True

    def run(self):
        wc = win32gui.WNDCLASS()
        wc.lpszClassName = 'test_devicenotify'
        wc.style = win32con.CS_GLOBALCLASS | win32con.CS_VREDRAW | win32con.CS_HREDRAW
        wc.hbrBackground = win32con.COLOR_WINDOW + 1
        wc.lpfnWndProc = {win32con.WM_HOTKEY: self.handle_hotkey}
        win32gui.RegisterClass(wc)

        # 產生一個不可見的視窗
        hwnd = win32gui.CreateWindow(wc.lpszClassName,
            'Testing some devices',
            win32con.WS_CAPTION,
            100, 100, 900, 900, 0, 0, 0, None)

        if not ctypes.windll.user32.RegisterHotKey(
            hwnd,
            42,
            win32con.MOD_ALT,
            0x46
        ):
            logging.warning('ALT+F is already registered by others.')

        # 開始 message pump，等待通知被傳遞
        while self.running:
            win32gui.PumpWaitingMessages()
        win32gui.DestroyWindow(hwnd)
        win32gui.UnregisterClass(wc.lpszClassName, None)


def main(argv):
    logging.basicConfig(
        filename=os.path.expanduser('~/.lig.log'),
        filemode='w',
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.DEBUG
    )
    try:
        app = Application(argv)
        STYLESHEET = 'style.css'
        app.setOrganizationName('helanic')
        app.setOrganizationDomain('answeror.com')
        app.setApplicationName('lit')
        app.setQuitOnLastWindowClosed(False)
        # style
        with open(STYLESHEET, 'r') as f:
            app.setStyleSheet(f.read())
        from go import Go
        from run import Run

        lit = Lit([Go(), Run()])
        lit.show()

        return app.exec_()
    except Exception as e:
        logging.error(e)


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
