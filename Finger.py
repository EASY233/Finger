#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author = EASY
import time
from config import config
from lib.cmdline import cmdline
from lib.checkenv import CheckEnv
from lib.output import Output
from lib.identify import Identify

if __name__ == '__main__':
    # 打印logo
    print(config.Banner)
    # 检测环境
    check = CheckEnv()
    # 加载参数
    cmdline()
    # 运行程序
    test = Identify()
    test.run()
    # # 保存数据
    save = Output()









