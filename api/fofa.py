#!/usr/bin/env python
# -*- coding: utf-8 -*-
import base64
import json
import random
from urllib.parse import quote

import requests

from config.data import logging
from lib.runtime import build_proxies


class FofaClient:
    def __init__(self, email, key, default_size=100, proxy_url='', user_agents=None):
        self.email = email or ''
        self.key = key or ''
        self.default_size = default_size
        self.proxy_url = proxy_url
        self.user_agents = tuple(user_agents or ())

    def _headers(self):
        user_agent = random.choice(self.user_agents) if self.user_agents else "Finger/6.0"
        return {"User-Agent": user_agent}

    def _proxies(self):
        return build_proxies(self.proxy_url)

    def is_configured(self):
        return bool(self.email and self.key)

    def validate_credentials(self):
        if not self.is_configured():
            raise RuntimeError("FOFA API 未配置，请检查 config/settings.py")

        auth_url = "https://fofa.info/api/v1/info/my?email={0}&key={1}".format(self.email, self.key)
        response = requests.get(auth_url, timeout=10, headers=self._headers(), proxies=self._proxies())
        if "{\"error\":false" not in response.text:
            raise RuntimeError("FOFA API 不可用，请检查配置是否正确")

    def search_web_assets(self, query, size=None):
        self.validate_credentials()
        size = size or self.default_size
        logging.info("正在调用fofa进行收集资产。。。。")
        logging.info("查询关键词为:{0},查询数量为:{1}".format(query, size))
        keyword = quote(str(base64.b64encode(query.encode()), encoding='utf-8'))
        url = (
            "https://fofa.info/api/v1/search/all?email={0}&key={1}&qbase64={2}"
            "&full=false&fields=protocol,host&size={3}"
        ).format(self.email, self.key, keyword, size)
        response = requests.get(url, timeout=10, headers=self._headers(), proxies=self._proxies())
        try:
            data = json.loads(response.text)
        except json.decoder.JSONDecodeError as exc:
            raise RuntimeError("FOFA 响应解析失败") from exc
        return self._extract_urls(data)

    def search_ip_web_assets(self, ip_targets, size=None):
        urls = []
        for ip in ip_targets:
            urls.extend(self.search_web_assets("ip={0}".format(ip), size=size))
        return urls

    @staticmethod
    def _extract_urls(payload):
        urls = []
        for item in payload.get("results", []):
            protocol = item[0]
            host = item[1]
            if "http" in host or "https" in host:
                url = host
            elif protocol in ("http", "https"):
                url = "{0}://{1}".format(protocol, host)
            elif protocol == "":
                url = "http://{0}".format(host)
            else:
                continue
            logging.info(url)
            urls.append(url)
        return urls
