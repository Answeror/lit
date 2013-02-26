#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
For some reason, calling a main() function to start the
application as in earlier examples produces a runtime error
when the application is closed:
    QObject::startTimer: QTimer can only be used with threads
        started with QThread

Start the application directly and no error occurs.

See <http://www.pyinmyeye.com/2012/01/qt-48-modelview-read-only-table-view.html> for deatils.
'''


from qt.QtGui import (
    QApplication,
    QWidget,
    QLineEdit,
    QVBoxLayout,
    QCompleter,
    QStringListModel,
    QKeyEvent,
    QAbstractItemView,
    QListView,
    QItemSelectionModel,
    QItemDelegate
)
from qt.QtCore import (
    Qt,
    QEvent,
    QTimer,
    QAbstractItemModel,
    QModelIndex,
    QMutex,
    QMutexLocker,
    QMetaObject,
    Slot
)
from qt import QT_API, QT_API_PYQT

from functools import partial
import os
import re
import ctypes
import logging
from common import set_app_info

from suggest import Suggest
from worker import Worker

# these config should be saved
MAX_LIST_LENGTH = 20
MAX_VISIBLE_ITEMS = 12


def winid(self):
    if QT_API == QT_API_PYQT:
        return self.winId()
    else:
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


def parse_query(text):
    if not text.startswith(';'):
        return None, text
    m = re.search(r';(\S*)( (.*)){0,1}', text)
    return m.group(1), m.group(2)[1:] if not m.group(2) is None else None


class Lit(QWidget):

    def __init__(self, worker, client):
        super(Lit, self).__init__()

        self.worker = worker
        self.client = client

        from go import Go
        from run import Run
        #from recent import Recent
        #from iciba import Iciba
        #from f import F
        #lit = Lit([Go(), Run(), Recent(), Iciba()])
        plugins = [
            Go(worker=worker, client=client),
            Run(worker=worker, client=client)
        ]

        lay = QVBoxLayout()

        # spacing of search box
        lay.setSpacing(0)
        lay.setMargin(0)

        self.inp = Input(self.act, self)
        self.inp.textChanged.connect(self._try_query)
        self.completer = Suggest(self.inp)
        #self.inp.setCompleter(self.completer)
        self.completer.activated[QModelIndex].connect(self.select)
        lay.addWidget(self.inp)
        self.setLayout(lay)
        self._install_plugins(plugins)
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.Popup
            | Qt.WindowStaysOnTopHint
        )
        self.setWindowTitle('lit')

        self.mutex = QMutex()

        self.jobs = []

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

    #def keyPressEvent(self, e):
        #if e.key() == Qt.Key_Escape and not self.inp.text():
            #e.accept()
            #self.close()
        #else:
            #e.ignore()

    def _move_to_center(self):
        desktop = QApplication.desktop()
        self.move(
            (desktop.width() - self.width()) // 2,
            (desktop.height() - self.height()) // 2
        )

    def resizeEvent(self, e):
        self._move_to_center()
        self.super.resizeEvent(e)

    def handle_hotkey(self):
        self.toggle_visibility()

    def toggle_visibility(self):
        logging.info("visible: {}".format(self.shown()))
        if self.shown():
            self.hide()
        else:
            self.show()

    def shown(self):
        #return self.isVisible() and not (self.windowState() & Qt.WindowMinimized)
        return self.isVisible()

    def showEvent(self, e):
        # show on top
        QTimer.singleShot(0, lambda: self.client.goto(hwnd(self)))
        super(Lit, self).showEvent(e)

    def _install_plugins(self, plugins):
        self.plugins = {p.name: p for p in plugins}
        self.default_plugin = plugins[0] if self.plugins else None
        self._setup_plugins()

    def _setup_plugins(self):
        for p in self.plugins.values():
            if hasattr(p, 'setup'):
                p.setup()

    def _teardown_plugins(self):
        for p in self.plugins.values():
            if hasattr(p, 'teardown'):
                p.teardown()

    def _try_query(self, text):
        """Avoid line editor frozen when key continues pressed."""
        QTimer.singleShot(0, lambda: self.query(text))

    def _clean_jobs(self):
        """Stop unfinished jobs, remove finished jobs from job list."""
        for job in self.jobs:
            job.try_stop()
        self.jobs = [job for job in self.jobs if not job.finished]

    def query(self, text):
        cmd, arg = parse_query(text)

        self.cmd = self.default_plugin.name if cmd is None else cmd
        if arg is None:
            self._reset_popup()
        else:
            plugin = None
            if cmd is None:
                if not self.default_plugin is None:
                    plugin = self.default_plugin
            else:
                if cmd in self.plugins:
                    plugin = self.plugins[cmd]
            if plugin:
                plugin.worker.clear()
                plugin.lit(
                    arg,
                    upper_bound=MAX_LIST_LENGTH,
                    finished=self._try_popup
                )

    def select(self, index):
        cmd = self.cmd
        self.hide()
        assert self.completer.content
        # make sure task switch after search box hide
        QTimer.singleShot(
            0,
            partial(
                self.plugins[cmd].select,
                content=self.completer.content,
                index=index
            )
        )

    def act(self):
        if self.cmd == 'exit':
            self._teardown_plugins()
            self.client.stop()
            QApplication.quit()
        if self.cmd in self.plugins:
            self.plugins[self.cmd].act()

    def _try_popup(self, content):
        # don't show popup if search box is hidden
        if self.isVisible():
            QTimer.singleShot(0, lambda: self.popup(content))

    def popup(self, content):
        with QMutexLocker(self.mutex):
            self.completer.complete(content)

    def _reset_popup(self):
        self.completer.reset()

    def showEvent(self, e):
        #QTimer.singleShot(0, lambda: windows.goto(hwnd(self)))
        self.inp.setFocus()
        if not self.completer.popuped:
            QTimer.singleShot(0, lambda: self._try_query(self.inp.text()))
        self.super.showEvent(e)

    def hideEvent(self, e):
        # block signals to avoid trigger completer update
        state = self.inp.blockSignals(True)
        try:
            self.inp.setText('')
        finally:
            self.inp.blockSignals(state)
        if self.completer.popuped:
            self.completer.hide_popup()
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


class RowDelegate(QItemDelegate):

    def __init__(self, parent):
        self.super.__init__(parent)

    @property
    def super(self):
        return super(QItemDelegate, self)

    def sizeHint(self, option, index):
        s = QItemDelegate.sizeHint(self, option, index)
        s.setHeight(s.height() + 10)
        return s


class CenterListView(QListView):
    """Always scroll to center."""

    def __init__(self, parent=None):
        self.super.__init__(parent)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        #self.setSpacing(2)
        #self.setItemDelegate(QStyledItemDelegate())
        #self.setItemDelegate(RowDelegate(self))

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
        #self.popup().setItemDelegate(RowDelegate(self))
        #self.popup().setItemDelegate(QStyledItemDelegate(self))
        self.setMaxVisibleItems(MAX_VISIBLE_ITEMS)
        if not parent is None:
            self.setWidget(parent)

    @property
    def popuped(self):
        return self.popup().isVisible()

    @property
    def super(self):
        return super(Completer, self)

    def update(self, result):
        if isinstance(result, QAbstractItemModel):
            model = result
        else:
            model = QStringListModel()
            model.setStringList([str(r) for r in result])

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
        #{
            #Qt.Key_Escape: lambda: self.setText(''),
            #Qt.Key_Return: self.enter
        #}.get(e.key(), lambda: None)()
        #super(Input, self).keyPressEvent(e)

        if e.key() == Qt.Key_Escape:
            if self.text():
                self.setText('')
                e.accept()
            else:
                e.ignore()
        elif e.key() == Qt.Key_Return:
            self.enter()
        else:
            super(Input, self).keyPressEvent(e)

    #def setCompleter(self, completer):
        #completer.setWidget(self)


def start_server():
    import subprocess as sp
    import os

    root = r'C:\Program Files (x86)\lit'
    #root = ''

    sp.call([
        os.path.join(root, 'ele', 'elevate.cmd'),
        os.path.join(root, 'litserver.exe')
    ])


if __name__ == '__main__':
    logging.basicConfig(
        filename=os.path.expanduser('~/.lit.log'),
        filemode='w',
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.DEBUG
    )
    client = None
    try:
        start_server()

        import sys
        argv = sys.argv
        app = QApplication(argv)
        STYLESHEET = 'style.css'
        set_app_info(app, 'lit')
        app.setQuitOnLastWindowClosed(False)

        # style
        with open(STYLESHEET, 'r') as f:
            app.setStyleSheet(f.read())

        worker = Worker()

        from client import Client
        client = Client()
        QMetaObject.invokeMethod(
            client,
            'start',
            Qt.QueuedConnection
        )

        lit = Lit(worker, client)
        client.toggle.connect(lit.handle_hotkey)
        client.connected.connect(lit.show)

        #return app.exec_()
        app.exec_()
    except Exception as e:
        logging.exception(e)
        if client:
            client.stop()


#if __name__ == '__main__':
    #import sys
    #main(sys.argv)
