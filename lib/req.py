#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author = EASY
import requests
import random
import codecs
import mmh3
from lib.IpFactory import IPFactory
from urllib.parse import urlsplit, urljoin
from config.data import Urls, Webinfo,Urlerror
from config import config
from lib.identify import Identify
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings()
from concurrent.futures import ThreadPoolExecutor


class Request:
    def __init__(self):
        Webinfo.result = []
        Urlerror.result = []
        self.checkcms = Identify()
        self.ipFactory = IPFactory()
        with ThreadPoolExecutor(config.threads) as pool:
            run = pool.map(self.apply, set(Urls.url))

    def apply(self, url):
        try:
            #proxies = { "http": "127.0.0.1:8080","https": "127.0.0.1:8080"}
            with requests.get(url, timeout=10, headers=self.get_headers(), cookies=self.get_cookies(), verify=False,
                              allow_redirects=True, stream=True) as response:
                if int(response.headers.get("content-length", default=1000)) > 100000:
                    self.response(url, response, True)
                else:
                    self.response(url, response)
        except KeyboardInterrupt:
            logger.error("用户强制程序，系统中止!")
            exit(0)
        except Exception as e:
            results = {"url": str(url), "cms": "-", "title": '-',
                       "status": "-", "Server": "-",
                       "size": "-", "iscdn": "-", "ip": "-",
                       "address": "-", "isp": "-"}

            Urlerror.result.append(results)
            pass

    def response(self, url, response, ignore=False):
        if ignore:
            html = ""
            size = response.headers.get("content-length", default=1000)
        else:
            response.encoding = response.apparent_encoding if response.encoding == 'ISO-8859-1' else response.encoding
            response.encoding = "utf-8" if response.encoding is None else response.encoding
            html = response.content.decode(response.encoding,"ignore")
            size = len(response.text)
        title = self.get_title(html).strip().replace('\r', '').replace('\n', '')
        status = response.status_code
        server = response.headers["Server"] if "Server" in response.headers else ""
        server = "" if len(server) > 50 else server
        faviconhash = self.get_faviconhash(url)
        iscdn, iplist = self.ipFactory.factory(url)
        iplist = ','.join(set(iplist))
        datas = {"url": url, "title": title, "body": html, "status": status, "Server": server, "size": size,
                 "header": response.headers, "faviconhash": faviconhash, "iscdn": iscdn, "ip": iplist,
                 "address": "", "isp": ""}
        self.checkcms.run(datas)

    def get_faviconhash(self, url):
        try:
            parsed = urlsplit(url)
            url = urljoin(parsed.scheme + "://" + parsed.netloc, "favicon.ico")
            response = requests.get(url, headers=self.get_headers(), timeout=4)
            favicon = codecs.encode(response.content, "base64")
            hash = mmh3.hash(favicon)
            return hash
        except:
            return 0

    def get_title(self, html):
        soup = BeautifulSoup(html, 'lxml')
        title = soup.title
        if title and title.text:
            return title.text
        if soup.h1:
            return soup.h1.text
        if soup.h2:
            return soup.h2.text
        if soup.h3:
            return soup.h3.text
        desc = soup.find('meta', attrs={'name': 'description'})
        if desc:
            return desc['content']

        word = soup.find('meta', attrs={'name': 'keywords'})
        if word:
            return word['content']

        text = soup.text
        if len(text) <= 200:
            return text
        return ''

    def get_headers(self):
        """
        生成伪造请求头
        """
        ua = random.choice(config.user_agents)
        headers = {
            'Accept': 'text/html,application/xhtml+xml,'
                      'application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': ua,
        }
        return headers

    def get_cookies(self):
        cookies = {'rememberMe': 'test'}
        return cookies

