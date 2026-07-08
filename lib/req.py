#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author = EASY233
# DEPRECATED: 已统一到 lib/finger.py，请使用 Finger 类替代 Request
# 保留此文件仅用于向后兼容
from config.data import Urls, Webinfo, Urlerror
from lib.finger import Finger


class Request:
    def __init__(self, urls=None, threads=None, timeout=None):
        target_urls = list(set(urls if urls is not None else getattr(Urls, 'url', [])))
        scanner = Finger(threads=threads)
        self.results = scanner.scan(target_urls, timeout=timeout)
        self.successes = [result for result in self.results if not result.get("error_type")]
        self.errors = [result for result in self.results if result.get("error_type")]

        # 向后兼容旧代码仍然读取全局结果容器的用法
        Webinfo.result = list(self.successes)
        Urlerror.result = list(self.errors)
