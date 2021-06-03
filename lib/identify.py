#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author = EASY
import os
import re
import json
from config.data import path
from config.color import color
from config.data import Urls,logging,Webinfo


class Identify:
     def __init__(self):
         filepath = os.path.join(path.library,'finger.json')
         with open(filepath, 'r', encoding='utf-8') as file:
             finger= json.load(file)
             for name,value in finger.items():
                 self.obj = value
             # 初始化指纹库
             self._prepare_app()

     def run(self,datas):
         self.datas = datas
         cms = self._has_app()
         if cms:
             self.datas["cms"] = str(set(cms)).replace("{","").replace("}","")
             Webinfo.result.insert(0,{"url": self.datas["url"], "cms": self.datas["cms"], "title": self.datas["title"],
                                    "status": self.datas["status"], "Server": self.datas['Server'],
                                    "size": self.datas["size"]})

         else:
             self.datas["cms"] = ""
             Webinfo.result.append({"url": self.datas["url"], "cms": self.datas["cms"], "title": self.datas["title"],
                                    "status": self.datas["status"], "Server": self.datas['Server'],
                                    "size": self.datas["size"]})

         Msg = "{0} {1} {2} {4} {3}".format(color.green(self.datas['cms']),
                                            color.blue(self.datas['Server']), self.datas['title'],
                                            color.yellow(self.datas['status']), self.datas["url"])
         logging.success(Msg)

     def _prepare_app(self):
         for line in self.obj:
             if "regula" == line["method"]:
                 self.obj[self.obj.index(line)]["keyword"] = self._prepare_pattern(line["keyword"][0])

     def _prepare_pattern(self, pattern):
         regex, _, rest = pattern.partition('\\;')
         try:
             return re.compile(regex, re.I)
         except re.error as e:
             return re.compile(r'(?!x)x')

     def _has_app(self):
         cms = []
         for line in self.obj:
             flag = 1
             if line['method'] == "faviconhash" and self.datas["faviconhash"] == line["keyword"][0]:
                 cms.append(line["cms"])
             elif line["method"] == "keyword":
                 for key in line["keyword"]:
                     if key not in  str(self.datas[line["location"]]):
                         flag = 0
                 if flag == 1:
                      cms.append(line["cms"])
             elif line["method"] == "regula":
                 if line["keyword"].search(self.datas[line["location"]]):
                     cms.append(line["cms"])
             else:
                 pass
         return cms



