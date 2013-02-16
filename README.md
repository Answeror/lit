# Lit

**version: 0.1.4**

## Introduction

Lit is a task switcher and launcher, used to replace `ALT`+`TAB` and `WIN`+`R`. The goal of this project is to make a desktop search platform and make everything searchable, i.e. tasks, executables, filenames, pdf contents and annotations, images, evernote...

Both task switching and launcher submodule use fuzzy search based on weighted Levenshtein distance.

### Snapshots

**Task switching** using `\g` command or query directly (default mode is `\g`):

![Task switch](http://dl.answeror.com/u/3450602/lit.go.png)

**Launcher** using `\r` command:

![Launcher](http://dl.answeror.com/u/3450602/lit.run.png)

## Install

### Requirements

* Windows (tested on win7 and win8 x64)
* Python3 (Cx-Freeze does not work on `3.3`)
* PyQt4
* Cx-Freeze
* Pywin32
* WMI

### From binary

[Download](http://code.google.com/p/yet-another-lit/downloads/list).

After install, you may need manually create a shotcut of `lit.exe`.

### From source

Create a virtualenv first, then install WMI:

```
pip install wmi
```

You can install cx-Freeze and pywin32 downloaded from [here](http://www.lfd.uci.edu/~gohlke/pythonlibs/) using easy_install.

For PyQt4, you must install it globally and copy it and sip to virutalenv `site-package` folder manually, or compile it on your own.

Clone this repo. Under the root folder:

```
python setup.py bdist_msi
```

The `msi` installer will be created under `dist` folder.

## Usage

Use `;;` to toggle search box (I'm a vimer, and accustomed to `jj`). Search text are make of two parts: command and query (optional, some command may haven't query part, like `\exit`), seperated by a space.

Command can be:

* `\r` (i.e. `\run`): run executable under your `PATH`
* `\g` (i.e. `\go`): task switch
* `\exit`: as it says

Default mode is `\g`, you can do task switch just without command part.

Use:

* arrow keys or `CTRL+J`/`CTRL+K` to navigate;
* `ESC` to clear search box (when popup shown) or hide it.

## Changelog

### 0.1.4

* New search algorithm, based on extended Levenshtein distance.
* Client/Server structure to provide minimum UAC requirement.
* Improved `\run` performance.
* Unified sync and async job interface.
