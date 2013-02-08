#!/usr/bin/env python
# -*- coding: utf-8 -*-

from qt.QtCore import (
    QThread,
    QObject,
    QCoreApplication,
    QMetaObject,
    Qt,
    Slot,
    Signal
)


class Job(QObject):

    finished = Signal()

    @Slot()
    def run(self):
        print("job thread: %d" % QThread.currentThreadId())
        self.finished.emit()


def finished():
    print("post thread: %d" % QThread.currentThreadId())


if __name__ == '__main__':
    import sys
    app = QCoreApplication(sys.argv)
    print("main thread: %d" % QThread.currentThreadId())
    thread = QThread()
    thread.start()
    job = Job()
    job.finished.connect(finished, Qt.QueuedConnection)
    job.moveToThread(thread)
    QMetaObject.invokeMethod(job, 'run', Qt.QueuedConnection)
    app.exec_()
    thead.wait()
