#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author = EASY233
import os
import warnings
from lib.cmdline import cmdline
from colorama import init as wininit
from lib.app import FingerApplication

# 过滤第三方库在新版 Python 下的 DeprecationWarning
warnings.filterwarnings("ignore", category=DeprecationWarning, module="xlsxwriter")

wininit(autoreset=True)

if __name__ == '__main__':
    from config import settings

    print(settings.Banner)
    app = FingerApplication()
    app.run(cmdline())
