#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author = EASY
import argparse
import platform
import sys
import os
from config.data import path,logging

class CheckEnv:
    def __init__(self):
        self.pyVersion = platform.python_version()
        self.path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        self.python_check()
        self.path_check()

    def python_check(self):
        if self.pyVersion < "3.6":
            logging.error("此Python版本 ('{0}') 不兼容,成功运行程序你必须使用版本 >= 3.6 (访问 ‘https://www.python.org/downloads/".format(self.pyVersion))
            exit(0)

    def path_check(self):
        try:
            os.path.isdir(self.path)
        except UnicodeEncodeError:
            errMsg = "your system does not properly handle non-ASCII paths. "
            errMsg += "Please move the project root directory to another location"
            logging.error(errMsg)
            exit(0)
        path.home = self.path
        path.output = os.path.join(self.path,'output')
        path.config = os.path.join(self.path,'config')
        if not os.path.exists(path.output):
            warnMsg = "The output folder is not created, it will be created automatically"
            logging.warning(warnMsg)
            os.mkdir(path.output)






