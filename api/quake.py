#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import random

import requests

from config.data import logging
from lib.runtime import build_proxies


class QuakeClient:
    def __init__(self, token, proxy_url='', user_agents=None):
        self.token = token or ''
        self.proxy_url = proxy_url
        self.user_agents = tuple(user_agents or ())

    def _headers(self):
        user_agent = random.choice(self.user_agents) if self.user_agents else "Finger/6.0"
        return {
            "User-Agent": user_agent,
            "X-QuakeToken": self.token,
        }

    def _proxies(self):
        return build_proxies(self.proxy_url)

    def validate_credentials(self):
        if not self.token:
            raise RuntimeError("请先在config/settings.py文件中配置quake的api")

    def search_web_assets(self, query, size):
        self.validate_credentials()
        if not query:
            raise RuntimeError("Quake 查询必须提供 --query")
        if not size:
            raise RuntimeError("Quake 查询必须提供 --size")

        logging.info("正在使用使用360 Quake进行资产收集。。。")
        logging.info("查询关键词为:{0},查询数量为:{1}".format(query, size))
        data = {
            "query": query,
            "start": 0,
            "size": size,
        }
        response = requests.post(
            url="https://quake.360.cn/api/v3/search/quake_service",
            headers=self._headers(),
            json=data,
            timeout=10,
            proxies=self._proxies(),
        )
        try:
            payload = json.loads(response.text)
        except json.decoder.JSONDecodeError as exc:
            raise RuntimeError("Quake 响应解析失败") from exc
        return self._extract_urls(payload)

    @staticmethod
    def _extract_urls(payload):
        urls = []
        if payload.get('code') != 0:
            raise RuntimeError("360 Quake API 查询失败: {0}".format(payload.get('message', 'unknown error')))

        for item in payload.get('data', []):
            port = "" if item['port'] in (80, 443) else ":{}".format(str(item['port']))
            service_name = item['service']['name']
            if service_name == 'http/ssl':
                url = 'https://' + item['service']['http']['host'] + port
            elif service_name == 'http':
                url = 'http://' + item['service']['http']['host'] + port
            else:
                continue
            logging.info(url)
            urls.append(url)
        return urls
