#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author = EASY
import argparse

def cmdline():
    parser = argparse.ArgumentParser(description="Finger scan --by EASY")
    target = parser.add_argument_group('Target')
    target.add_argument('-u',dest='url',type=str,help="Input your url target")
    target.add_argument('-f',dest='file',type=str,help="Input your target's file")
    output = parser.add_argument_group('Output')
    output.add_argument('-o',dest='output',type=str,default="html",help="Select the output format.eg(html,json,xls,default:html)")
    db = parser.add_argument_group("DB")
    db.add_argument("-type",dest="type",type=str,default="",help="Select how you want to query")
    db.add_argument("-key",dest="key",type=str,default="",help="search for the keyword")
    args = parser.parse_args()
    usage = '''
    Usage: python3 {} -u http://www.baidu.com
    Usage: python3 {} -f urls.txt
    '''.format(parser.prog,parser.prog)
    return args

