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
    Slot,
    QModelIndex,
    QAbstractItemModel,
    QTime,
    QTimer
)
import stream as sm
import re
import pyHook
import win32gui
import ctypes
import windows
from win32con import SW_RESTORE


_QWidget_winId = QWidget.winId


def winid(self):
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
        self.completer = Completer()
        self.inp.setCompleter(self.completer)
        self.completer.activated.connect(self.select)
        lay.addWidget(self.inp)
        self.setLayout(lay)
        self._install_plugins(plugins)
        self.setWindowFlags(Qt.FramelessWindowHint)

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

    def toggle_visibility(self):
        if self.window_shown():
            self.hide_window()
        else:
            self.show_window()

    def window_shown(self):
        return self.isVisible() and not (self.windowState() & Qt.WindowMinimized)

    def hide_window(self):
        self.inp.setText('')
        self.setWindowState(self.windowState() | Qt.WindowMinimized)
        #self.hide()

    def show_window(self):
        #self.show()
        windows.goto(hwnd(self))

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
        self.hide_window()
        self.plugins[self.cmd].select(text)

    def act(self):
        if self.cmd == 'exit':
            QApplication.quit()
        if self.cmd in self.plugins:
            self.plugins[self.cmd].act()

    #def minimize(self):
        #self.setWindowState(Qt.WindowMinimized)

    def popup(self, items):
        self.completer.update(items)

    def showEvent(self, e):
        if not self.completer.popuped:
            QTimer.singleShot(0, lambda: self.query(self.inp.text()))
        self.super.showEvent(e)


#class CircularListView(QListView):
    #"""Provide circular selection."""

    #def __init__(self):
        #self.super.__init__()
        #self.setSelectionMode(QAbstractItemView.SingleSelection)

    #@property
    #def super(self):
        #return super(CircularListView, self)

    #@property
    #def atbottom(self):
        #return self.currentIndex().row() + 1 == self.model().rowCount()

    #@property
    #def attop(self):
        #return self.currentIndex().row() == 0

    #def event(self, e):
        #print(e.type())
        #if e.type() == QEvent.KeyPress:
            #print(self.atbottom, e.key())
            #if self.attop and e.key() == Qt.Key_Up:
                #QApplication.postEvent(self, QKeyEvent(
                    #QEvent.KeyPress,
                    #Qt.Key_End,
                    #e.modifiers()
                #))
                #return True
            #elif self.atbottom and e.key() == Qt.Key_Down:
                #QApplication.postEvent(self, QKeyEvent(
                    #QEvent.KeyPress,
                    #Qt.Key_Home,
                    #e.modifiers()
                #))
                #return True
        #return self.super.event(e)

    #def moveCursor(self, action, modifiers):
        #if self.attop and action == self.MoveUp:
            #action = self.MoveEnd
        #elif self.atbottom and action == self.MoveDown:
            #action = self.MoveHome
        #return self.super.moveCursor(action, modifiers)

    #@Slot(QModelIndex, QModelIndex)
    #def currentChanged(self, current, previous):
        #if not current.isValid():
            #smodel = self.selectionModel()
            #imodel = smodel.model()
            #if imodel.rowCount() > 0:
                #if previous.row() == 0:
                    #correct = imodel.index(imodel.rowCount() - 1, 0)
                #else:
                    #correct = imodel.index(0, 0)
                #smodel.setCurrentIndex(
                    #correct,
                    #QItemSelectionModel.Select
                #)


class Completer(QCompleter):
    """Custom completer for avaiable tasks."""

    def __init__(self, parent=None):
        super(Completer, self).__init__(parent=parent)
        self.windows = []

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

    def keyPressEvent(self, e):
        {
            Qt.Key_Escape: lambda: self.setText(''),
            Qt.Key_Return: self.enter
        }.get(e.key(), lambda: None)()
        super(Input, self).keyPressEvent(e)

    def setCompleter(self, completer):
        completer.setWidget(self)


class HotkeyScope(object):

    def __init__(self, down=None, up=None):
        self.down = down
        self.up = up

    def __enter__(self):
        self.hooks = pyHook.HookManager()
        if not self.down is None:
            self.hooks.KeyDown = self.down
        if not self.up is None:
            self.hooks.KeyUp = self.up
        self.hooks.HookKeyboard()
        return self

    def __exit__(self, *args):
        self.hooks.UnhookKeyboard()


def main(argv):
    app = QApplication(argv)
    STYLESHEET = 'style.css'
    app.setOrganizationName('helanic')
    app.setOrganizationDomain('answeror.com')
    app.setApplicationName('lit')
    # style
    with open(STYLESHEET, 'r') as f:
        app.setStyleSheet(f.read())
    from go import Go

    lit = Lit([Go()])

    def key_down(e):
        CTRL = 162
        CAP = 20
        TAB = 9
        # alt + tab
        if e.Alt and e.KeyID == TAB:
            lit.toggle_visibility()
            return False
        return True

    with HotkeyScope(down=key_down):
        lit.show()
        return app.exec_()


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
