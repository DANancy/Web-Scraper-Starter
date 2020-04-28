#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# load .env variables
from dotenv import load_dotenv
import os
from pathlib import Path

# import libs
from pymongo import MongoClient
import random
from fake_useragent import UserAgent

# DB connection
env_path = Path('..') / '.env'
load_dotenv(dotenv_path=env_path)
myClient = MongoClient(os.getenv("DBCONNECT"))
table = myClient['ProxyDB']['active_proxy']
ua = UserAgent()

class ProxyManager:
    def __init__(self):
        self.lst = list(table.find())
        random.shuffle(self.lst)

    def get_proxy(self):
        proxyInfo = self.lst[0]
        if proxyInfo == None:
            raise NoProxyException("No Proxy Available")
        proxyHost = proxyInfo['proxyHost']
        proxyPort = proxyInfo['proxyPort']
        proxyMate = "http://{}:{}".format(proxyHost, proxyPort)
        ips = {
            "http": proxyMate,
            "https": proxyMate
        }
        return ips

    def invalid_proxy(self):
        self.lst.pop(0)

class NoProxyException(Exception):
    pass

myProxy = ProxyManager()