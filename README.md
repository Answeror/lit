# Lit

**version: 0.1.2**

## Introduction

Lit is a task switcher and launcher, used to replace `ALT`+`TAB` and `WIN`+`R`. The goal of this project is to make a desktop search platform and make everything searchable, i.e. tasks, executables, filenames, pdf contents and annotations, images, evernote...

Both task switching and launcher submodule use fuzzy search based on weighted Levenshtein distance.

### Snapshots

**Task switching** using `\g` command or query directly (default mode is `\g`):

![Task switch](http://dl.answeror.com/u/3450602/lit.go.png)\ 

**Launcher** using `\r` command:

![Launcher](http://dl.answeror.com/u/3450602/lit.run.png)\ 

## Install

### Requirements

* Windows (only tested on win7 x64)
* Python3
* PyQt4
* cx-Freeze
* pywin32
* [stream.py](http://github.com/Answeror/stream.py) (py3k version)

### From binary

Download [v0.1.1](http://dl.answeror.com/u/3450602/lit-0.1.1-win32.msi).

After install, you may need manually create a shotcut of `lit.exe`.

### From source

Install PyQt4, cx-Freeze, pywin32 is fairly easy (indeed some pain if you want install them in the virtualenv like me, but it is **possible**).

For stream.py:

```
pip install git+https://github.com/Answeror/stream.py.git
```

And then clone this repo. Under the root folder:

```
python setup.py bdist_msi
```

The `msi` installer will be created under `dist` folder.

## Usage

Use `ALT`+`F` to toggle search box. Search text are make of two parts: command and query (optional, some command may haven't query part, like `\exit`), seperated by a space.

Command can be:

* `\r` (i.e. `\run`): run executable under your `PATH`
* `\g` (i.e. `\go`): task switch
* `\exit`: as it says

Default mode is `\g`, you can do task switch just without command part.
