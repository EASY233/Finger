#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author = EASY
import os
import re
import json
from lib.req import Request
from urllib.parse import urljoin
from config.data import path
from config import config
from config.color import color
from config.data import Urls,logging,Webinfo
from concurrent.futures import ThreadPoolExecutor


class Identify:
    def __init__(self):
        self.urls = Urls.url
        self.name = []
        filepath = os.path.join(path.library,'end.json')
        with open(filepath,'r',encoding='utf-8') as file:
            obj = json.load(file)
        # 初始化指纹库
        for line in obj:
            if line['name'] not in self.name:
                self.name.append(line)
            self._prepare_app(line)
        Msg = "成功加载{0}指纹库,共加载指纹{1}".format(filepath,len(self.name))
        logging.success(Msg)
        Msg = "是否开启了MD5指纹识别:{0}".format(config.checkmd5)
        logging.success(Msg)
        self.fingers = obj
        self.req = Request()
        self.md5 = config.checkmd5

    def _prepare_app(self,app):
        for key in ['url','html','script']:
            value = app.get(key)
            if value is None:
                app[key] = []
            else:
                if not isinstance(value,list):
                    app[key] = [value]
        for key in ['headers','meta']:
            value = app.get(key)
            if value is None:
                app[key] = {}

        for key in ['url', 'html', 'script']:
            app[key] = [self._prepare_pattern(pattern) for pattern in app[key]]

        for key in ['headers', 'meta']:
            obj = app[key]
            for name, pattern in obj.items():
                obj[name] = self._prepare_pattern(obj[name])
        for key in ['matches']:
            value = app.get(key)
            if value  is None:
                pass
            else:
                if 'keyword' in value.keys():
                    app[key]['keyword'] = self._prepare_pattern(value['keyword'])

    def _prepare_pattern(self, pattern):
        regex, _, rest = pattern.partition('\\;')
        try:
            return re.compile(regex, re.I)
        except re.error as e:
            return re.compile(r'(?!x)x')


    def _has_app(self,app,target):
        if "matches" in app.keys() and self.md5 and "md5" in target.keys():
            for name,value in app['matches'].items():
                if name == 'md5':
                    if app['matches']['md5'].lower() == target['md5'].lower():
                        self.flag = 1
                        return True
                if name == 'keyword':
                    if app['matches']['keyword'].search(target['html']):
                        self.flag = 1
                        return True
        for regex in app['url']:
            if regex.search(target['html']):
                return True
        for name,regex in  app['headers'].items():
            if name in target['headers'].keys():
                content = target['headers'][name]
                if regex.search(content):
                    return True
        for regex in app['script']:
            for script in target['scripts']:
                if regex.search(script):
                    return True
        for name, regex in app['meta'].items():
            if name in target['meta']:
                content = target['meta'][name]
                if regex.search(content):
                    return True

        for regex in app['html']:
            if regex.search(target['html']):
                return True


    def Judge(self,url):
        _target = self.req.apply(url)
        self.flag = 0
        detected_apps = {"Application":"","Language":"","Server":"","System":""}
        for line in self.fingers:
            try:
                target = _target[url]
                self.title = target['title']
                self.status = target['status']
                if "matches" in line.keys() and self.md5 and self.status == 200 and detected_apps["Application"] == "":
                    if 'url' in line['matches'].keys():
                        full_url = urljoin(url, line['matches']['url'])
                        if 'md5' in line['matches'].keys():
                            if full_url in _target.keys():
                                target = _target[full_url]
                            else:
                                target = self.req.apply(full_url,True)[full_url]
            except Exception as e:
                pass
            if self._has_app(line,target):
                if line['cats'] == "Application":
                    detected_apps['Application'] = line['name']
                if line['cats'] == "Language":
                    detected_apps['Language'] = line['name']
                if line['cats'] == "Server":
                    detected_apps['Server'] = line['name']
                if line['cats'] == "System":
                    detected_apps['System'] = line['name']
            if self.flag:
                break
        detected_apps['title'] = self.title
        detected_apps['status'] = self.status
        Msg = "{0} {1} {2} {4} {3}".format(color.green(detected_apps['Application']),color.blue(detected_apps['Server']),detected_apps['title'],color.yellow(detected_apps['status']),url)
        logging.info(Msg)
        Webinfo.result[url] = detected_apps

    def run(self):
        with ThreadPoolExecutor(config.threads) as pool:
            for url in self.urls:
                pool.submit(self.Judge, url)