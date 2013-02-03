#!/usr/bin/env python
# -*- coding: utf-8 -*-


from qt.QtGui import (
    QWidget,
    QApplication,
    QAbstractItemView,
    QStringListModel,
    QItemSelectionModel,
    QTreeView,
    QKeyEvent
)
from qt.QtCore import (
    Qt,
    QTimer,
    QPoint,
    QObject,
    pyqtSignal,
    QEvent,
    QModelIndex,
    QAbstractItemModel
)
import stream as sm


MAX_ITEM = 7


class CenterListView(QTreeView):
    """Always scroll to center."""

    def __init__(self, parent=None):
        super(CenterListView, self).__init__(parent)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setRootIsDecorated(False)
        self.setHeaderHidden(True)

    def scrollTo(self, index, _):
        """Always scroll to center."""
        super(CenterListView, self).scrollTo(index, QAbstractItemView.PositionAtCenter)

    def showEvent(self, e):
        QTimer.singleShot(0, self._adjust_popup_height)
        super(CenterListView, self).showEvent(e)

    def _adjust_popup_height(self):
        if self.isVisible():
            if self.model().rowCount(QModelIndex()) <= MAX_ITEM:
                vsb = self.verticalScrollBar()
                if vsb and vsb.isVisible():
                    self.resize(self.width(), self.height() + 1)
                    QTimer.singleShot(0, self._adjust_popup_height)


class Suggest(QWidget):

    activated = pyqtSignal(QModelIndex)

    def __init__(self, parent):
        QObject.__init__(self, parent)
        self.editor = parent
        self.popup = None
        self.set_popup(CenterListView())
        self.content = None

    def set_popup(self, popup):
        if self.popup:
            self.popup.removeEventFilter(self)

        self.popup = popup
        popup.setWindowFlags(Qt.Popup)
        popup.setFocusPolicy(Qt.NoFocus)
        #popup.setFocusProxy(self.editor)
        popup.setMouseTracking(True)

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
                #self.editor.setFocus()
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

    @property
    def model(self):
        return self.popup.model() if self.popup else None

    @model.setter
    def model(self, value):
        self.popup.setModel(value)

    def hide_popup(self):
        self.popup.hide()

    def reset(self):
        """Reset model and hide popup."""
        self.model = QStringListModel()
        self.hide_popup()

    def select_first_item(self):
        first_index = self.popup.model().index(0, 0)
        self.popup.selectionModel().setCurrentIndex(
            first_index,
            QItemSelectionModel.Select | QItemSelectionModel.Rows
        )
        self.popup.scrollTo(first_index, QAbstractItemView.PositionAtCenter)

    def _resize_popup(self):
        h = self.popup.sizeHintForRow(0) * min(MAX_ITEM, self.row_count)
        self.popup.resize(self.editor.width(), h)
        #hsb = self.popup.horizontalScrollBar()
        #if hsb and hsb.isVisible():
            #h += hsb.sizeHint().height()
        self.popup.move(self.editor.mapToGlobal(QPoint(0, self.editor.height())))

    @property
    def row_count(self):
        return self.model.rowCount(QModelIndex())

    @property
    def empty(self):
        return self.row_count == 0

    def complete(self, content):
        if content is None:
            logging.debug('Content should not be None...')
            content = []

        # cache content
        self.content = content

        # make model
        if isinstance(content, QAbstractItemModel):
            model = content
        else:
            model = QStringListModel()
            model.setStringList(content >> sm.map(str) >> list)

        self.model = model

        if self.empty:
            # no suggestion, hide
            self.hide_popup()
        else:
            #self.popup.setFocus()
            self._resize_popup()
            self.select_first_item()
            self.popup.show()
            #self._continues_update()

    def _update_popup(self):
        model = self.model
        self.model = None
        self.model = model

    def _continues_update(self):
        if self.popuped:
            self._update_popup()
            QTimer.singleShot(1000, self._continues_update)
