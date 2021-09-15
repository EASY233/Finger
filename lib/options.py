#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author = EASY
import os
from api.fofa import Fofa
from api.quake import Quake
from config.data import Urls, logging, Save, Ips


class initoptions:
    def __init__(self, args):
        Urls.url = []
        Ips.ip = []
        self._url = args.url
        self._file = args.file
        self._ip = args.ip
        self._ipfile = args.ipfile
        self.format = args.output
        # 查询顺序非常重要不能随便移动位置
        self.api_data(args)
        self.target()
        self.output()
        self.get_ip()

    def api_data(self, args):
        if args.fofa:
            run = Fofa()
        elif args.quake:
            run = Quake()

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

    def check(self, url):
        if not url.startswith('http'):
            # 若没有http头默认同时添加上http与https到目标上
            Urls.url.append("http://" + str(url))
            Urls.url.append("https://" + str(url))
        else:
            Urls.url.append(url)

    def output(self):
        if self.format not in ["json", "xlsx"]:
            errMsg = "Ouput args is error,eg(json,xlsx default:xlsx)"
            logging.error(errMsg)
            exit(0)
        Save.format = self.format

    def get_ip(self):
        try:
            if self._ip:
                if "-" in self._ip:
                    start, end = [self.ip_num(x) for x in self._ip.split('-')]
                    iplist = [self.num_ip(num) for num in range(start, end + 1) if num & 0xff]
                    for ip in iplist:
                        Ips.ip.append(ip)
                else:
                    Ips.ip.append(self._ip)
            elif self._ipfile:
                if os.path.exists(self._ipfile):
                    with open(self._ipfile, 'r') as file:
                        for i in file:
                            i = i.strip()
                            if "-" in i:
                                start, end = [self.ip_num(x) for x in i.split('-')]
                                iplist = [self.num_ip(num) for num in range(start, end + 1) if num & 0xff]
                                for ip in iplist:
                                    Ips.ip.append(ip)
                            else:
                                Ips.ip.append(i)
                else:
                    errMsg = "File {0} is not find".format(self._ipfile)
                    logging.error(errMsg)
                    exit(0)
            if Ips.ip:
                run = Fofa()
        except Exception as e:
            logging.error(e)
            logging.error("IP格式有误，正确格式为192.168.10.1,192.168.10.1/24 or 192.168.10.10-192.168.10.50")
            exit(0)

    def ip_num(self, ip):
        ip = [int(x) for x in ip.split('.')]
        return ip[0] << 24 | ip[1] << 16 | ip[2] << 8 | ip[3]

    def num_ip(self, num):
        return '%s.%s.%s.%s' % ((num & 0xff000000) >> 24,
                                (num & 0x00ff0000) >> 16,
                                (num & 0x0000ff00) >> 8,
                                num & 0x000000ff)
