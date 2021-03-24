#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author = EASY
#from gevent import monkey,pool;monkey.patch_all()
from concurrent.futures import ThreadPoolExecutor
import requests
import random
import chardet
from config import config
from config.color import color
from lib.Wappalyzer import Wappalyzer
from config.data import Urls,logging,Webinfo
from bs4 import BeautifulSoup

def run():
    logging.info("The total number of targets:{0}".format(len(Urls.url)))
    logging.info("The number of threads:{}".format(config.threads))
    test = Request()
    test.run()



class Request:
    def __init__(self):
        self.urls = Urls.url
        self.app = None
        self.Wappalyzer =Wappalyzer()


    def request(self,url):
        try:
            response = requests.get(url, timeout=1, headers=self.get_headers(), cookies=self.get_cookies(),
                             allow_redirects=True)
            url_info = self.response(url,response)
        except Exception as e:
            pass

    def response(self,url,response):
        response_content = response.content
        html = response_content.decode(encoding=chardet.detect(response_content)['encoding'])
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
        app_info = self.Wappalyzer.run(response.url,html,response.headers,scripts,meta)
        Webinfo.result[url] = {"title":title,"status":status,"size":size,"App_Info":app_info}
        for name, value in app_info.items():
            if name == "Application":
                self.app = value
                break
            else:
                self.app = None
        msg = "{0} {4} {1} {2} {3}".format(color.green(str(self.app)), color.yellow(status), url, color.cyan(title),color.blue(app_info['Server']))
        logging.success(msg)


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



    def run(self):
        #gevent_pool = pool.Pool(config.threads)
        #gevent_pool.map(self.request,self.urls)
        with ThreadPoolExecutor(config.threads) as pool:
            for url in self.urls:
                pool.submit(self.request, url)
        logging.info("Task is done!")






