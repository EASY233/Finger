#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author = EASY
import os
from config.data import path
from config.data import Webinfo
from lib.ip2Region import Ip2Region


class IpAttributable:
    def __init__(self):
        dbFile = os.path.join(path.library, "data", "ip2region.db")
        self.searcher = Ip2Region(dbFile)
        self.getAttributable()


    def ipCollection(self):
        ip_list = []
        for value in Webinfo.result:
            if value["iscdn"] == 0 and value["ip"] not in ip_list:
                ip_list.append(value["ip"])
        return ip_list

    def getAttributable(self):
        ips = self.ipCollection()
        try:
            for ip in ips:
                addr = []
                data = str(self.searcher.binarySearch(ip)["region"].decode('utf-8')).split("|")
                isp = data[4].replace("0", "")
                data.pop(4)
                data.pop(1)
                for ad in data:
                    if ad != "0" and ad not in addr and "" != ad:
                        addr.append(ad)
                address = ','.join(addr)
                for value in Webinfo.result:
                    if value['ip'] == ip:
                        Webinfo.result[Webinfo.result.index(value)]["address"] = address
                        Webinfo.result[Webinfo.result.index(value)]["isp"] = isp
        except Exception as e:
            pass

