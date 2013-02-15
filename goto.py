#!/usr/bin/env python
# -*- coding: utf-8 -*-


import windows
import socket


ENCODING = 'utf-8'
PORT = 50007


def main(argv):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', PORT))
    s.listen(1)
    conn, addr = s.accept()
    while True:
        line = conn.recv(1024).decode(ENCODING)
        if line == 'exit':
            break
        elif line == 'all':
            print(windows.top_level_windows())
        else:
            windows.goto(int(line))
            print(line)


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
else:
    import subprocess as sp
    import sys
    import os
    import logging

    root = r'C:\Program Files (x86)\lit'

    p = sp.Popen([
        os.path.join(root, 'ele', 'elevate.cmd'),
        os.path.join(root, 'goto.exe')
    ])
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            s.connect((socket.gethostname(), PORT))
        except:
            pass
        else:
            break

    def goto(hwnd):
        s.sendall(('%d\n' % hwnd).encode(ENCODING))
