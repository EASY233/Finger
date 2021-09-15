#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author = EASY
import os
import re
import json
import socket
import ipaddress
from urllib.parse import urlsplit
from lib.ip2Region import Ip2Region
from config.data import path


class IPFactory:
    def __init__(self):
        cdnFile = os.path.join(path.library, 'cdn_ip_cidr.json')
        dbFile = os.path.join(path.library, "data", "ip2region.db")
        self.searcher = Ip2Region(dbFile)
        with open(cdnFile, 'r', encoding='utf-8') as file:
            self.cdns = json.load(file)

    def parse_host(self,url):
        host = urlsplit(url).netloc
        if ':' in host:
            host = re.sub(r':\d+', '', host)
        return host

    def factory(self, url):
        try:
            ip_list = []
            host = self.parse_host(url)
            items = socket.getaddrinfo(host, None)
            for ip in items:
                if ip[4][0] not in ip_list:
                    ip_list.append(ip[4][0])
            if len(ip_list) > 1:
                return 1, ip_list
            else:
                for cdn in self.cdns:
                    if ipaddress.ip_address(ip_list[0]) in ipaddress.ip_network(cdn):
                        return 1, ip_list
            return 0, ip_list
        except Exception as e:
            return 0, ip_list

