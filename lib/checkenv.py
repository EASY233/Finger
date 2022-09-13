#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author = EASY
import platform
import os
import time
import requests
import hashlib
from config.config import head,FingerPrint_Update
from config.data import path,logging

class CheckEnv:
    def __init__(self):
        self.pyVersion = platform.python_version()
        self.path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        self.python_check()
        self.path_check()
        if FingerPrint_Update:
            self.update()

    def python_check(self):
        if self.pyVersion < "3":
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
        path.library = os.path.join(self.path, 'library')
        if not os.path.exists(path.output):
            warnMsg = "The output folder is not created, it will be created automatically"
            logging.warning(warnMsg)
            os.mkdir(path.output)

    def update(self):
        try:
            is_update = True
            nowTime = time.strftime("%Y%m%d%H%M%S", time.localtime())
            logging.info("正在在线更新指纹库。。")
            Fingerprint_Page = "https://cdn.jsdelivr.net/gh/EASY233/Finger/library/finger.json"
            response = requests.get(Fingerprint_Page,timeout = 10,headers = head)
            filepath = os.path.join(path.library,"finger.json")
            bakfilepath = os.path.join(path.library,"finger_{}.json.bak".format(nowTime))
            with open(filepath,"rb") as file:
                if hashlib.md5(file.read()).hexdigest() == hashlib.md5(response.content).hexdigest():
                    logging.info("指纹库已经是最新")
                    is_update = False
            if is_update:
                logging.info("检查到指纹库有更新,正在同步指纹库。。。")
                os.rename(filepath,bakfilepath)
                with open(filepath,"wb") as file:
                    file.write(response.content)
                with open(filepath,'rb') as file:
                    Msg = "更新成功！" if hashlib.md5(file.read()).hexdigest() == hashlib.md5(response.content).hexdigest() else "更新失败"
                    logging.info(Msg)
        except Exception as e:
            logging.warning("在线更新指纹库失败！")







