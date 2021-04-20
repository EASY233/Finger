#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author = EASY
import argparse
import os
from lib.sql import Save
from config.data import Urls,logging,Save,Db

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
    Usage: python3 {} -u http://www.baidu.com or www.baidu.com
    Usage: python3 {} -f urls.txt
    '''.format(parser.prog,parser.prog)
    initoption(args)

def initoption(args):
    url = args.url
    file = args.file
    Db.type = args.type
    Db.key = args.key
    output = args.output
    Urls.url = []
    if url:
        if not url.startswith('http'):
            _u = "http://" + str(_url)
            _urls = "https://" + str(_url)
            Urls.url.append(_u)
            Urls.url.append(_urls)
        else:
            Urls.url.append(_url)
    if file:
        if os.path.exists(file):
            with open(file,'r') as f:
                for i in f:
                    _url = i.strip('\n')
                    if not _url.startswith('http'):
                        _url = "http://" + str(_url)
                    Urls.url.append(_url)
        else:
            errMsg = "File {0} is not find".format(file)
            logging.error(errMsg)
            exit(0)
    if output not in ["html","json","xls"]:
        errMsg = "Ouput args is error,eg(html,json,csv default:html)"
        logging.error(errMsg)
        exit(0)
    Save.format = output
