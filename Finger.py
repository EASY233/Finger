#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author = EASY
from config import config
from lib.cmdline import cmdline
from lib.checkenv import CheckEnv
from lib.req import Request
from lib.output import Output
from lib.identify import Identify
from lib.options import initoptions
from lib.sql import Save

if __name__ == '__main__':
    # 打印logo
    print(config.Banner)
    # 检测环境
    check = CheckEnv()
    # 加载参数
    options = initoptions(cmdline())
    run = Request()
    # # 运行程序
    # test = Identify()
    # test.run()
    # # # 保存数据
    # dbsave = Save()
    save = Output()








