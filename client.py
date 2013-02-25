#!/usr/bin/env python
# -*- coding: utf-8 -*-


from qt.QtCore import (
    QObject,
    Signal,
    Slot,
    QDataStream
)
from qt.QtNetwork import (
    QTcpSocket,
    QHostAddress
)
from service import (
    set_version,
    write,
    PORT
)


class Client(QObject):

    toggle = Signal()
    connected = Signal()

    def __init__(self, parent=None):
        super(Client, self).__init__(parent)

        self._make_socket()

    def _make_socket(self):
        self.con = QTcpSocket(self)
        self.con.readyRead.connect(self._handle_read)
        self.con.connected.connect(self.connected)

    def _handle_read(self):
        ins = QDataStream(self.con)
        set_version(ins)
        line = str(ins.readString(), encoding='ascii')
        if line == 'toggle':
            self.toggle.emit()

    @Slot()
    def start(self):
        connect = lambda: self.con.connectToHost(QHostAddress.LocalHost, PORT)
        connect()
        while not self.con.waitForConnected(-1):
            logging.error('connect to host error: {}'.format(self.con.error()))
            connect()

    def stop(self):
        self.con.disconnectFromHost()

    def _write(self, callback):
        assert self.con
        write(self.con, callback)

    def goto(self, hwnd):
        self._write(lambda out: out.writeString(('goto %d' % int(hwnd)).encode('ascii')))

    def close_window(self, hwnd):
        self._write(lambda out: out.writeString(('close %d' % int(hwnd)).encode('ascii')))
