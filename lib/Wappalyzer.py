#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author = EASY
import re
import os
import json
from config.data import path

class Wappalyzer:
    def __init__(self):
        filepath = os.path.join(path.config,'apps.json')
        with open(filepath,'r',encoding='utf-8') as file:
            obj = json.load(file)
        self.apps = obj['apps']
        for name,app in  self.apps.items():
            self._prepare_app(app)
        self.url = ''
        self.html = ''
        self.headers = ''
        self.scripts = ''
        self.meta = ''


    def _prepare_app(self,app):
        for key in ['url','html','script','impolies']:
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

    def _prepare_pattern(self, pattern):
        regex, _, rest = pattern.partition('\\;')
        try:
            return re.compile(regex, re.I)
        except re.error as e:
            return re.compile(r'(?!x)x')

    def _has_app(self,app):
        for regex in app['url']:
            if regex.search(self.url):
                return True
        for name,regex in  app['headers'].items():
            if name in self.headers:
                content = self.headers[name]
                if regex.search(content):
                    return True
        for regex in app['script']:
            for script in self.scripts:
                if regex.search(script):
                    return True
        for name, regex in app['meta'].items():
            if name in self.meta:
                content = self.meta[name]
                if regex.search(content):
                    return True

        for regex in app['html']:
            if regex.search(self.html):
                return True

    def run(self,url,html,headers,scripts,meta):
        detected_apps = {"Application":"","Language":"","Server":""}
        self.url = url
        self.html = html
        self.headers = headers
        self.scripts = scripts
        self.meta = meta
        for app_name,app in self.apps.items():
            if self._has_app(app):
                if app['cats']  in detected_apps:
                    detected_apps[app['cats']] = app_name
        return detected_apps
