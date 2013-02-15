#!/usr/bin/env python
# -*- coding: utf-8 -*-


from qt.QtCore import (
    QByteArray,
    QDataStream,
    QIODevice
)


PORT = 50007


def set_version(s):
    s.setVersion(QDataStream.Qt_4_0)


def write(con, callback):
    block = QByteArray()
    out = QDataStream(block, QIODevice.WriteOnly)
    set_version(out)
    callback(out)
    con.write(block)
