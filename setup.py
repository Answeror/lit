#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cx_Freeze import setup, Executable
from command import cmds


includes = ['pyHook._cpyHook']
excludes = []
packages = []

setup(
        name='lit',
        version='0.1.0',
        cmdclass=cmds,
        options={
            'build_exe': {
                'packages': packages,
                'includes': includes,
                'excludes': excludes,
                'include_files': ['style.css']
                }
            },
        executables=[Executable(
            'lit.py',
            base='Win32GUI',
            targetName='lit.exe',
            compress=True,
            icon='icons/48.ico'
            )]
        )
