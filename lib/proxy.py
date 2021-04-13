#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author = EASY
import requests
from concurrent.futures import ThreadPoolExecutor
from config.data import logging
import ssl
import json


ssl._create_default_https_context = ssl._create_unverified_context

class Proxyinfo:
    def __init__(self):
        self.proxylist = []
        self.getproxylist()
        self.run()

    def getproxylist(self):
        url = "http://proxylist.fatezero.org/proxy.list"
        context = requests.get(url,timeout=5).text
        for line in context.split('\n'):
            try:
                data = json.loads(line, strict=False)
                ip_port = {}
                ip_port[data['type']] = "{0}:{1}".format(data['host'],data['port'])
                self.proxylist.append(ip_port)
            except:
                pass


    def checkip(self,target):
        for name,value in target.items():
            proxy = {
                name: value
            }
            url = "https://httpbin.org/ip"
            try:
                r = requests.get(url,timeout = 3,proxies=proxy)
                if r.status_code == 200 and value.split(":")[0] in r.text:
                    print(value)
            except:
                pass
    def run(self):
        Msg = "共获取到代理ip:{0}".format(len(self.proxylist))
        logging.info(Msg)
        logging.info("正在检测ip质量")
        with ThreadPoolExecutor(20) as pool:
            for url in self.proxylist:
                pool.submit(self.checkip, url)






Proxyinfo()