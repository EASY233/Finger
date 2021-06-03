#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author = EASY
import requests
import random
import codecs
import mmh3
import chardet
from urllib.parse import urlsplit,urljoin
from config.data import Urls,Webinfo
from config import config
from lib.identify import Identify
from bs4 import BeautifulSoup
import urllib3
urllib3.disable_warnings()
from concurrent.futures import ThreadPoolExecutor

class Request:
    def __init__(self):
        Webinfo.result = []
        self.checkcms = Identify()
        with ThreadPoolExecutor(config.threads) as pool:
            run = pool.map(self.apply,Urls.url)


    def apply(self,url):
        try:
            proxies = {'http': 'http://127.0.0.1:8080', 'https': 'https://127.0.0.1:8080'}
            response = requests.get(url, timeout=5, headers=self.get_headers(), cookies=self.get_cookies(),verify=False,allow_redirects=True)
            self.response(url,response)
        except Exception as e:
            pass

    def response(self,url,response):
        response_content = response.content
        response.encoding = response.apparent_encoding if response.encoding == 'ISO-8859-1' else response.encoding
        html = response.content.decode(response.encoding)
        title = self.get_title(html).strip().replace('\r', '').replace('\n', '')
        status = response.status_code
        size = len(response.text)
        if "Server" in response.headers:
            Server = response.headers["Server"]
        else:
            Server = ""
        faviconhash = self.get_faviconhash(url)
        datas = {"url":url,"title":title,"body":html,"status":status,"Server":Server,"size":size,"header":response.headers,"faviconhash":faviconhash}
        self.checkcms.run(datas)

    def get_faviconhash(self,url):
        try:
            parsed = urlsplit(url)
            url = urljoin(parsed.scheme+"://"+parsed.netloc,"favicon.ico")
            response = requests.get(url,headers=self.get_headers())
            favicon = codecs.encode(response.content, "base64")
            hash = mmh3.hash(favicon)
            return hash
        except:
            return 0


    def get_title(self,html):
        soup = BeautifulSoup(html, 'lxml')
        title = soup.title
        if title and title.text:
            return title.text
        h1 = soup.h1
        if h1:
            return h1.text

        h2 = soup.h2
        if h2:
            return h2.text

        h3 = soup.h3
        if h2:
            return h3.text

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
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/68.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) '
            'Gecko/20100101 Firefox/68.0',
            'Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/68.0']
        ua = random.choice(user_agents)
        headers = {
            'Accept': 'text/html,application/xhtml+xml,'
                      'application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
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

