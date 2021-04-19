#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author = EASY
import requests
import random
import chardet
import hashlib
from bs4 import BeautifulSoup
import urllib3
urllib3.disable_warnings()

class Request:
    def __init__(self):
        self.app = None
        self.datas = {}
        self.md5 = True


    def apply(self,url,md5=False):
        try:
            response = requests.get(url, timeout=1, headers=self.get_headers(), cookies=self.get_cookies(),
                             allow_redirects=True,verify=False)
            self.response(url,response,md5)
            return self.datas
        except Exception as e:
            pass

    def response(self,url,response,md5=False):
        response_content = response.content
        if chardet.detect(response_content)['encoding']:
            html = response_content.decode(encoding=chardet.detect(response_content)['encoding'])
        else:
            html = response.text
        title = self.get_title(html).strip().replace('\r', '').replace('\n', '')
        status = response.status_code
        size = len(response.text)
        soup = BeautifulSoup(html,'html.parser')
        scripts = [script['src'] for script in soup.findAll('script', src=True)]
        meta = {
            meta['name'].lower():
                meta['content'] for meta in soup.findAll(
                'meta', attrs=dict(name=True, content=True))
        }
        if md5:
            self.datas[url] = {"html": html, "title":title,"status":status,"headers": response.headers, "scripts": scripts, "meta": meta,"md5":hashlib.md5(response.content).hexdigest()}
        else:
            self.datas[url] = {"html": html, "title":title,"status":status,"headers": response.headers, "scripts": scripts, "meta": meta}
    def get_title(self,html):
        soup = BeautifulSoup(html, 'lxml')
        title = soup.title
        if title:
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
            'Referer': 'https://www.google.com/',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': ua,
        }
        return headers

    def get_cookies(self):
        cookies = {'rememberMe': 'test'}
        return cookies

