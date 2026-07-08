#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author = EASY233

import random

Version = "V6.1"
Author = "EASY233"
Banner = '\033[1;31m\n' + r'''
______ _
|  ___(_)
| |_   _ _ __   __ _  ___ _ __
|  _| | | '_ \ / _` |/ _ \ '__|
| |   | | | | | (_| |  __/ |
\_|   |_|_| |_|\__, |\___|_|
                __/ |
               |___/           ''' + '\033[1;34mVersion: {0}\n\n    Author: {1}\033[0m                   \n'.format(Version, Author)

# 设置线程数，默认30
threads = 30

# HTTP请求超时（秒），默认5
timeout = 5


# 设置Fofa key信息
Fofa_email = ""
Fofa_key = ""
Fofa_Size = 100
# 普通会员API查询数据是前100，高级会员是前10000条根据自已的实际情况进行调整。

# 设置360quake key信息，每月能免费查询3000条记录
QuakeKey = ""


# 是否选择在线跟新指纹库，默认为True每次程序都会检查一遍指纹库是否是最新
FingerPrint_Update = False


user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:135.0) '
            'Gecko/20100101 Firefox/135.0',
            'Mozilla/5.0 (X11; Linux x86_64; rv:135.0) Gecko/20100101 Firefox/135.0']


def get_random_headers():
    """生成随机请求头，每次调用使用不同的 User-Agent"""
    return {
        "User-Agent": random.choice(user_agents),
        "Accept-Encoding": "gzip, deflate",
    }


def get_proxies():
    """从全局配置读取代理地址，构建 requests 兼容的 proxies 字典"""
    from config.data import Proxy
    proxy_url = getattr(Proxy, 'url', '')
    if not proxy_url:
        return None
    return {"http": proxy_url, "https": proxy_url}
