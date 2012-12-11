#!/usr/bin/env python
# -*- coding: utf-8 -*-


from PyQt4.QtGui import\
        QWidget,\
        QApplication,\
        QTreeWidget,\
        QFrame,\
        QTreeWidgetItem,\
        QAbstractItemView,\
        QStringListModel,\
        QItemSelectionModel,\
        QListView,\
        QKeyEvent
from PyQt4.QtCore import\
        Qt,\
        QPoint,\
        QObject,\
        pyqtSignal,\
        pyqtSlot,\
        QEvent,\
        QModelIndex,\
        QTimer,\
        QThreadPool,\
        QMetaObject,\
        QAbstractItemModel
import stream as sm


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


class Suggest(QWidget):

    activated = pyqtSignal(QModelIndex)

    def __init__(self, parent):
        QObject.__init__(self, parent)
        self.editor = parent
        self.popup = None
        self.set_popup(CenterListView())
        #self.editor.installEventFilter(self)

    def set_popup(self, popup):
        if self.popup:
            self.popup.removeEventFilter(self)

        self.popup = popup
        popup.setWindowFlags(Qt.Popup)
        popup.setFocusPolicy(Qt.NoFocus)
        #popup.setFocusProxy(self.editor)
        #popup.setMouseTracking(True)

        popup.installEventFilter(self)

        popup.clicked.connect(self.activated)
        self.activated.connect(popup.hide)

    def completionModel(self):
        return self.model

    def done(self, index):
        if index.isValid():
            self.activated.emit(index)

    def eventFilter(self, o, e):
        #if e.type() == QEvent.MouseButtonPress:
            ##self.popup.hide()
            #self.editor.setFocus()
            #return True

        if o == self.popup:
            if not self.popup.underMouse() and e.type() in (
                QEvent.MouseButtonPress,
                #QEvent.MouseButtonRelease,
                #QEvent.MouseButtonDblClick,
                #QEvent.MouseMove
            ):
                self.popup.hide()
                self.editor.setFocus()
                #QApplication.sendEvent(self.editor, e)
                return True
            elif e.type() == QEvent.KeyPress:
                key = e.key()
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
                elif key in (Qt.Key_Enter, Qt.Key_Return):
                    self.done(self.popup.currentIndex())
                    return True
                #elif key in (Qt.Key_Escape, ):
                    #self.editor.setFocus()
                    #self.popup.hide()
                    #return True
                #elif key in (
                    #Qt.Key_Home,
                    #Qt.Key_End,
                #):
                    #QApplication.sendEvent(self.editor, e)
                    #return True
                #elif key in (
                        #Qt.Key_Up,
                        #Qt.Key_Down,
                        #Qt.Key_Home,
                        #Qt.Key_End,
                        #Qt.Key_PageUp,
                        #Qt.Key_PageDown
                        #):
                    #pass
                else:
                    #self.editor.setFocus()
                    #self.editor.event(e)
                    #TODO: why HOME and END not processed by editor?
                    QApplication.sendEvent(self.editor, e)
                    #self.popup.hide()

        return self.super.eventFilter(o, e)

    @property
    def atbottom(self):
        p = self.popup
        return p.currentIndex().row() + 1 == p.model().rowCount(QModelIndex())

    @property
    def attop(self):
        return self.popup.currentIndex().row() == 0

    @property
    def popuped(self):
        return self.popup.isVisible()

    @property
    def super(self):
        return super(QWidget, self)

    def hide_popup(self):
        self.popup.hide()

    def update(self, result):
        if isinstance(result, QAbstractItemModel):
            model = result
        else:
            model = QStringListModel()
            model.setStringList(result >> sm.map(str) >> list)

        self.model = model
        self.popup.setModel(model)

        row_count = model.rowCount(QModelIndex())
        if row_count == 0:
            # no suggestion, hide
            self.popup.hide()
        else:
            h = self.popup.sizeHintForRow(0) * min(7, row_count) + 3
            self.popup.resize(self.editor.width(), h)
            self.popup.move(self.editor.mapToGlobal(QPoint(0, self.editor.height())))
            #self.popup.setFocus()
            self.popup.show()

            first_index = self.popup.model().index(0, 0)
            self.popup.selectionModel().setCurrentIndex(
                first_index,
                QItemSelectionModel.Select | QItemSelectionModel.Rows
            )
            self.popup.scrollTo(first_index, QAbstractItemView.PositionAtCenter)
