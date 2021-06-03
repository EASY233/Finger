#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author = EASY
import os
from config.data import Urls,logging,Save


class initoptions:
    def __init__(self,args):
        Urls.url = []
        self._url = args.url
        self._file = args.file
        self.format = args.output
        self.target()
        self.output()
    def target(self):
        if self._url:
            self.check(self._url)
        elif self._file:
            if os.path.exists(self._file):
                with open(self._file, 'r') as f:
                    for i in f:
                        self.check(i.strip())
            else:
                errMsg = "File {0} is not find".format(self._file)
                logging.error(errMsg)
                exit(0)

    def check(self,url):
        if not url.startswith('http'):
            # 若没有http头默认同时添加上http与https到目标上
            Urls.url.append("http://" + str(url))
            Urls.url.append("https://" + str(url))
        else:
            Urls.url.append(url)


    def output(self):
        if self.format not in ["html", "json", "xls"]:
            errMsg = "Ouput args is error,eg(html,json,csv default:html)"
            logging.error(errMsg)
            exit(0)
        Save.format = self.format
