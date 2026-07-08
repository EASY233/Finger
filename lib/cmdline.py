#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author = EASY233
import argparse

def cmdline():
    parser = argparse.ArgumentParser(description="Finger V6.1 — 红队资产存活探测与重点攻击系统指纹识别工具")
    target = parser.add_argument_group('Target')
    target.add_argument('-u',dest='url',type=str,help="Input your url target")
    target.add_argument('-f',dest='file',type=str,help="Input your target's file")
    ip = parser.add_argument_group('IP')
    ip.add_argument('-i',dest="ip",type=str,help="Input your ip target(127.0.0.1 , 127.0.0.1/24 or 127.0.0.10-127.0.0.45)")
    ip.add_argument('-if',dest='ipfile',type=str,help="Input your ip's file")
    api = parser.add_argument_group("Api")
    api.add_argument("-fofa",action="store_true",default=False,help="Select fofa to query data")
    api.add_argument("-quake",action="store_true",default=False,help="Select 360 Quake to query data")
    api.add_argument('--query', dest='api_query', type=str, default="", help="Asset query string for FOFA/Quake")
    api.add_argument('--size', dest='api_size', type=int, default=None, help="Asset query result size")
    extra = parser.add_argument_group('Extra')
    extra.add_argument('--cdn',action="store_true",default=False,help="Enable CDN detection (default: off)")
    extra.add_argument('--geo',action="store_true",default=False,help="Enable IP geolocation (default: off)")
    extra.add_argument('--audit',action="store_true",default=False,help="Enable rule quality audit after scan")
    proxy = parser.add_argument_group('Proxy')
    proxy.add_argument('--proxy',dest='proxy',type=str,default="",help="Proxy (http://127.0.0.1:8080 or socks5://127.0.0.1:1080)")
    output = parser.add_argument_group('Output')
    output.add_argument('-o',dest='output',type=str,default="xlsx",help="Select the output format.eg(json,xlsx,default:xlsx)")
    args = parser.parse_args()
    return args
