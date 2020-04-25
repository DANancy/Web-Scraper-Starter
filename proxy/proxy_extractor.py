#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# import scraper libs
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from fake_useragent import UserAgent

# import libs
from datetime import datetime
import sys
from pymongo import MongoClient

# load .env variables
import os
from dotenv import load_dotenv
from pathlib import Path

# DB connection
env_path = Path('..') / '.env'
load_dotenv(dotenv_path=env_path)
myClient = MongoClient(os.getenv("DBCONNECT"))
ua = UserAgent()
table = myClient['ProxyDB']['active_proxy']
table_new = myClient['ProxyDB']['active_proxy']

def proxies_extractor():
    # if you need proxy, setup yourself following the below example
    # myProxy = os.getenv("PROXYIP")
    # prox = Proxy()
    # prox.proxy_type = ProxyType.MANUAL
    # prox.socks_proxy = myProxy
    # prox.socks_version = os.getenv("SOCKETVERSION")
    # capabilities = webdriver.DesiredCapabilities.CHROME
    # prox.add_to_capabilities(capabilities)
    # opts = Options()
    # opts.add_argument("user-agent={}".format(ua['google chrome']))
    # browser = webdriver.Chrome(desired_capabilities=capabilities, chrome_options=opts)

    browser = webdriver.Chrome()
    browser.get('http://freeproxylists.net')

    page = 1
    while True:
        items = browser.find_elements(By.XPATH, '//*[@class="DataGrid"]//tr[position()>1]')
        for i in items:
            try:
                if len(i.text) != 0:
                    proxy = {}
                    proxyInfo = i.text.split(' ')
                    proxy['proxyHost'] = proxyInfo[0]
                    proxy['proxyPort'] = proxyInfo[1]
                    proxy['proxyProtocol'] = proxyInfo[2]
                    proxy['proxyAnonymity'] = proxyInfo[3]
                    proxy['insert time'] = datetime.now().isoformat()
                    print(proxy, page)
                    table.insert_one(proxy)
            except OSError as err:
                print("OS error: {0}".format(err))
            except:
                print("Unexpected error:", sys.exc_info())

        try:
            next = browser.find_element(By.XPATH, '//*[@class="page"]/a[last()]')
            if 'Next' not in next.text:
                raise NoSuchElementException
        except NoSuchElementException:
            break
        next.click()
        print('before wait')
        WebDriverWait(browser,30).until(
            EC.presence_of_element_located((By.XPATH, '//*[@class="page"]/a[last()]')))
        print('after wait')
        page += 1



def active_proxies(url):
    proxylst = table.find()
    for i in proxylst:
        proxy = {}
        header = {'User-Agent': ua['google chrome']}
        proxyHost = i['proxyHost']
        proxyPort = i['proxyPort']
        proxyProtocol = i['proxyProtocol']
        proxyMate = "http://{}:{}".format(proxyHost, proxyPort)
        ips = {
            "http": proxyMate,
            "https": proxyMate
        }
        try:
            resp = requests.get(url, header, proxies=ips)
            print(resp)
            if resp.status_code == 200:
                proxy['proxyHost'] = proxyHost
                proxy['proxyPort'] = proxyPort
                proxy['proxyProtocol'] = proxyProtocol
                proxy['test time'] = datetime.now().isoformat()
                proxy['response code'] = '200'
                table_new.insert_one(proxy)
        except OSError as err:
            print("OS error: {0}".format(err))
        except ValueError:
            print("Could not convert data to an integer.")
        except:
            print("Unexpected error:", sys.exc_info())

