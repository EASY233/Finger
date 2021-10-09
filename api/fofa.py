#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author = EASY
import json
import base64
import random
import requests
from urllib.parse import quote
from config.data import logging,Urls,Ips
from config.config import Fofa_key,Fofa_email,Fofa_Size,user_agents

class Fofa:
    def __init__(self):
        self.email = Fofa_email
        self.key = Fofa_key
        self.size = Fofa_Size
        self.headers = {
            "User-Agent": random.choice(user_agents)
        }
        if self.check():
            if Ips.ip:
                for ip in Ips.ip:
                    ip = "ip={}".format(ip)
                    self.run(ip)
            else:
                keyword = input("请输入查询关键词:").strip()
                self.run(keyword)
        else:
            logging.error("fofa api不可用，请检查配置是否正确！")

    def run(self,keyword):
        logging.info("正在调用fofa进行收集资产。。。。")
        logging.info("查询关键词为:{0},查询数量为:{1}".format(keyword,self.size))
        keyword = quote(str(base64.b64encode(keyword.encode()), encoding='utf-8'))
        url = "https://fofa.so/api/v1/search/all?email={0}&key={1}&qbase64={2}&full=false&fields=protocol,host&size={3}".format(
            self.email, self.key, keyword, self.size)
        try:
            response = requests.get(url,timeout=10,headers = self.headers )
            datas = json.loads(response.text)
            if "results" in datas.keys():
                for data in datas["results"]:
                    _url = ""
                    if "http" == data[0] or "https" == data[0]:
                        _url = "{0}://{1}".format(data[0], data[1])
                    elif "http" in data[1] or "https" in data[1]:
                        _url = data[1]
                    elif "" is data[0]:
                        _urll = "{0}://{1}".format("http", data[1])
                    if _url:
                        logging.info(_url)
                        Urls.url.append(_url)

        except requests.exceptions.ReadTimeout:
            logging.error("请求超时")
        except requests.exceptions.ConnectionError:
            logging.error("网络超时")
        except json.decoder.JSONDecodeError:
            logging.error("获取失败，请重试")
        except:
            logging.error("获取失败")
            pass

    def check(self):
        try:
            if self.email and self.key:
                auth_url = "https://fofa.so/api/v1/info/my?email={0}&key={1}".format(self.email, self.key)
                response = requests.get(auth_url, timeout=10, headers=self.headers)
                if self.email in response.text:
                    return True
                else:
                    return False
            else:
                return False
        except:
            return False
