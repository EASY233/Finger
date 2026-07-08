#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author = EASY233
import os
from config.data import logging
from lib.ip2region import Searcher
from lib.ip2region.util import IPv4


class IpAttributable:
    def __init__(self, results, library_dir):
        dbFile = os.path.join(library_dir, "data", "ip2region.xdb")
        self.results = results
        self.searcher = Searcher(IPv4, dbFile, None, None)
        self.getAttributable()
        self.searcher.close()


    def ipCollection(self):
        ip_list = []
        for value in self.results:
            ip = value.get("ip", "")
            if value.get("iscdn") == 0 and ip and ',' not in ip and ip not in ip_list:
                ip_list.append(ip)
        return ip_list

    def getAttributable(self):
        ips = self.ipCollection()
        for ip in ips:
            try:
                result = self.searcher.search(ip)
            except Exception as e:
                logging.warning("IP归属地查询失败: {0} → {1}".format(ip, str(e)))
                continue

            if not result:
                continue

            addr = []
            # v3 格式: 国家|省份|城市|ISP|国家代码
            data = result.split("|")
            isp = data[3].replace("0", "") if len(data) > 3 else ""
            for i, ad in enumerate(data):
                if i == 4:  # 跳过国家代码
                    continue
                if ad != "0" and ad not in addr and ad != "":
                    addr.append(ad)
            address = ','.join(addr)
            for value in self.results:
                if value.get('ip') == ip:
                    value["address"] = address
                    value["isp"] = isp
        return self.results
