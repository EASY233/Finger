#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author = EASY


Version = "V3.0"
Author = "EASY"
Website = "https://www.easy233.top"
Banner = '''\033[1;31m
______ _                       
|  ___(_)                      
| |_   _ _ __   __ _  ___ _ __ 
|  _| | | '_ \ / _` |/ _ \ '__|
| |   | | | | | (_| |  __/ |   
\_|   |_|_| |_|\__, |\___|_|    
                __/ |          
               |___/           \033[1;34mVersion: {0}

    Author: {1}
    Website: {2}\033[0m                   
'''.format(Version,Author,Website)

# 设置线程数，默认20
threads = 20
# 是否开启通过md5进行指纹识别，默认关闭
checkmd5 = False
# 是否把数据指纹识别数据自动添加到数据库中，默认开启
Dbsave = True