#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author = EASY
class Colored():
    def __init__(self):
        self.Red = '\033[1;31m'  # 红色
        self.Green = '\033[1;32m'  # 绿色
        self.Yellow = '\033[1;33m'  # 黄色
        self.Blue = '\033[1;34m'  # 蓝色
        self.Fuchsia = '\033[1;35m'  # 紫红色
        self.Cyan = '\033[1;36m'  # 青蓝色
        self.White = '\033[1;37m'  # 白色
        self.Reset = '\033[0m'  # 终端默认颜色

    def red(self, s):
        return "{0}{1}{2}".format(self.Red, s, self.Reset)

    def green(self, s):
        return "{0}{1}{2}".format(self.Green, s, self.Reset)

    def yellow(self, s):
        return "{0}{1}{2}".format(self.Yellow, s, self.Reset)

    def blue(self, s):
        return "{0}{1}{2}".format(self.Blue, s, self.Reset)

    def fuchsia(self, s):
        return "{0}{1}{2}".format(self.Fuchsia, s, self.Reset)

    def cyan(self, s):
        return "{0}{1}{2}".format(self.Cyan, s, self.Reset)

    def white(self, s):
        return "{0}{1}{2}".format(self.White, s, self.Reset)

color = Colored()
