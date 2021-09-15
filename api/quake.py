#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author = EASY
import json
import random
import requests
from config.data import Urls, logging
from config.config import QuakeKey, user_agents


class Quake:
    def __init__(self):
        self.headers = {
            "User-Agent": random.choice(user_agents),
            "X-QuakeToken": QuakeKey
        }
        if QuakeKey == "":
            logging.warning("请先在config/config.py文件中配置quake的api")
            exit(0)
        self.keywords = input("请输入查询关键词:").strip()
        self.size = input("请输入查询数量:").strip()
        if self.keywords == "" or self.size == "":
            logging.warning("查询关键词或者查询数量不能为空")
            exit(0)
        self.data = {
            "query": self.keywords,
            "start": 0,
            "size": self.size
        }
        logging.info("正在使用使用360 Quake进行资产收集。。。")
        logging.info("查询关键词为:{0},查询数量为:{1}".format(self.keywords, self.size))
        self.run()

    def run(self):
        try:
            response = requests.post(url="https://quake.360.cn/api/v3/search/quake_service", headers=self.headers,
                                     json=self.data, timeout=10)
            datas = json.loads(response.text)
            if len(datas['data']) >= 1 and datas['code'] == 0:
                for data in datas['data']:
                    if 'http/ssl' == data['service']['name']:
                        url = 'https://' + data['service']['http']['host'] + ':' + str(data['port'])
                        logging.info(url)
                        Urls.url.append(url)
                    elif 'http' == data['service']['name']:
                        url = 'http://' + data['service']['http']['host'] + ':' + str(data['port'])
                        logging.info(url)
                        Urls.url.append(url)
        except Exception as e:
            pass
