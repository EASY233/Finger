#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author = EASY
from config import config
from lib.cmdline import cmdline
from lib.checkenv import CheckEnv
from lib.req import Request
from lib.output import Output
from lib.Fofa import  Fofa
from colorama import init as wininit
from lib.options import initoptions
wininit(autoreset=True)

if __name__ == '__main__':
    # 打印logo
    print(config.Banner)
    # 检测环境
    check = CheckEnv()
    # 加载参数
    options = initoptions(cmdline())
    fofa = Fofa()
    run = Request()
    save = Output()








