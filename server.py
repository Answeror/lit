
#!/usr/bin/env python
# -*- coding: utf-8 -*-


import windows
from qt.QtCore import (
    QCoreApplication,
    QObject,
    QDataStream,
    QMetaObject,
    Qt,
    QThread,
    Signal,
    Slot
)
from qt.QtNetwork import (
    QTcpServer,
    QHostAddress
)
import logging
from service import (
    set_version,
    write,
    PORT
)
from common import set_app_info


class Server(QObject):

    def __init__(self, parent=None):
        super(Server, self).__init__(parent)

        self._make_tcp_server()

        self.hotkey_thread = HotkeyThread()
        self.hotkey_thread.fire.connect(self._handle_hotkey)

    def _make_tcp_server(self):
        self.s = QTcpServer(self)
        self.s.newConnection.connect(self._handle_connect)
        self.con = None

    def _handle_connect(self):
        self.con = self.s.nextPendingConnection()
        self.con.readyRead.connect(self._handle_read)
        self.con.disconnected.connect(self._handle_disconnect)
        logging.info('connected')

    def _handle_disconnect(self):
        self.con.deleteLater()
        QCoreApplication.quit()

    def _write(self, callback):
        assert self.con
        write(self.con, callback)

    def _handle_hotkey(self):
        logging.info('toggle')
        self._write(lambda out: out.writeString(b'toggle'))

    def _handle_read(self):
        ins = QDataStream(self.con)
        set_version(ins)
        line = str(ins.readString(), encoding='ascii')
        logging.info(line)
        windows.goto(int(line))

    @Slot()
    def start(self):
        self.hotkey_thread.start()

        if not self.s.listen(QHostAddress.LocalHost, PORT):
            logging.error(
                "Unable to start the server: %s." %
                self.tcpServer.errorString()
            )
            return


class HotkeyThread(QThread):

    fire = Signal()

    def __init__(self):
        QThread.__init__(self)
        from hotkey import Hotkey
        self.hotkey = Hotkey(self.handle_hotkey)

    def handle_hotkey(self):
        self.fire.emit()

    def stop(self):
        self.hotkey.stop()

    def run(self):
        self.hotkey.start()


if __name__ == '__main__':
    import sys
    import os
    logging.basicConfig(
        filename=os.path.expanduser('~/.lit.server.log'),
        filemode='w',
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.DEBUG
    )
    app = QCoreApplication(sys.argv)
    set_app_info(app, 'litserver')
    server = Server()
    QMetaObject.invokeMethod(
        server,
        'start',
        Qt.QueuedConnection
    )
    sys.exit(app.exec_())
