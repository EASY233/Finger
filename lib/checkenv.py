#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author = EASY233
import platform
import os
import time
import requests
import hashlib
from config import settings
from config.data import logging
from lib.runtime import RuntimePaths, build_proxies, default_root_dir

class CheckEnv:
    def __init__(self, root_dir=None):
        self.pyVersion = platform.python_version()
        self.paths = RuntimePaths.from_root(root_dir or default_root_dir())
        self.python_check()
        self.path_check()

    def python_check(self):
        if self.pyVersion < "3":
            logging.error("此Python版本 ('{0}') 不兼容,成功运行程序你必须使用版本 >= 3.6 (访问 ‘https://www.python.org/downloads/".format(self.pyVersion))
            raise SystemExit(1)

    def path_check(self):
        try:
            os.path.isdir(self.paths.root_dir)
        except UnicodeEncodeError:
            errMsg = "your system does not properly handle non-ASCII paths. "
            errMsg += "Please move the project root directory to another location"
            logging.error(errMsg)
            raise SystemExit(1)
        if not os.path.exists(self.paths.output_dir):
            warnMsg = "The output folder is not created, it will be created automatically"
            logging.warning(warnMsg)
            os.mkdir(self.paths.output_dir)

    def update(self, proxy_url=''):
        try:
            is_update = True
            nowTime = time.strftime("%Y%m%d%H%M%S", time.localtime())
            logging.info("正在在线更新指纹库。。")
            Fingerprint_Page = "https://cdn.jsdelivr.net/gh/EASY233/Finger/library/finger.json"
            response = requests.get(
                Fingerprint_Page,
                timeout=10,
                headers=settings.get_random_headers(),
                verify=False,
                proxies=build_proxies(proxy_url),
            )
            response.raise_for_status()
            content_type = str(response.headers.get("Content-Type", "")).lower()
            if "json" not in content_type:
                raise ValueError(f"unexpected content-type: {content_type or '-'}")
            filepath = os.path.join(self.paths.library_dir, "finger.json")
            bakfilepath = os.path.join(self.paths.library_dir, "finger_{}.json.bak".format(nowTime))
            json.loads(response.content.decode('utf-8'))
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




