#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author = EASY
import argparse

def cmdline():
    parser = argparse.ArgumentParser(description="Finger 一款红队在大量的资产中存活探测与重点攻击系统指纹探测工具 --by EASY")
    target = parser.add_argument_group('Target')
    target.add_argument('-u',dest='url',type=str,help="Input your url target")
    target.add_argument('-f',dest='file',type=str,help="Input your target's file")
    ip = parser.add_argument_group('IP')
    ip.add_argument('-i',dest="ip",type=str,help="Input your ip target(127.0.0.1 , 127.0.0.1/24 or 127.0.0.10-127.0.0.45)")
    ip.add_argument('-if',dest='ipfile',type=str,help="Input your ip's file")
    api = parser.add_argument_group("Api")
    api.add_argument("-fofa",action="store_true",default=False,help="Select fofa to query data")
    api.add_argument("-quake",action="store_true",default=False,help="Select 360 Quake to query data")
    output = parser.add_argument_group('Output')
    output.add_argument('-o',dest='output',type=str,default="xlsx",help="Select the output format.eg(json,xlsx,default:xlsx)")
    args = parser.parse_args()
    return args

