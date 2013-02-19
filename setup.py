#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cx_Freeze import setup, Executable
from command import cmds
import glob


includes = []
excludes = []
packages = []

setup(
    name='lit',
    version='0.1.5',
    install_requires=[
        'wmi',
        'pywin32'
    ],
    cmdclass=cmds,
    options={
        'build_exe': {
            'packages': packages,
            'includes': includes,
            'excludes': excludes,
            'include_files': ['style.css', 'AutoItX3.dll'] + glob.glob('ele/*')
        }
    },
    executables=[
        Executable(
            'lit.py',
            base='Win32GUI',
            targetName='lit.exe',
            compress=True,
            icon='icons/48.ico'
        ),
        Executable(
            'server.py',
            base='Win32GUI',
            targetName='litserver.exe',
            compress=True
        )
    ]
)
