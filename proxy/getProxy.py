#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# load .env variables
from dotenv import load_dotenv
import os
from pathlib import Path

# import scraper libs
from selenium import webdriver
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

# DB connection
env_path = Path('..') / '.env'
load_dotenv(dotenv_path=env_path)
myClient = MongoClient(os.getenv("DBCONNECT"))
ua = UserAgent()


def proxies_extractor(db):
    table = myClient[db]['proxy']

    myProxy = "192.168.0.248:1080"
    prox = Proxy()
    prox.proxy_type = ProxyType.MANUAL
    prox.socks_proxy = myProxy
    prox.socks_version = 5

    capabilities = webdriver.DesiredCapabilities.CHROME
    prox.add_to_capabilities(capabilities)
    opts = Options()
    opts.add_argument("user-agent={}".format(ua['google chrome']))
    browser = webdriver.Chrome(desired_capabilities=capabilities, chrome_options=opts)
    browser.get('http://freeproxylists.net')

    page = 1
    while True:
        next = browser.find_element(By.XPATH, '//*[@class="page"]/a[last()]')
        items = browser.find_elements(By.XPATH, '//*[@class="DataGrid"]//tr[position()>1]')
        if next != None:
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
                except ValueError:
                    print("Could not convert data to an integer.")
                except:
                    print("Unexpected error:", sys.exc_info())
            next.click()
            print('before wait')
            WebDriverWait(browser, 240).until(
                EC.presence_of_element_located((By.XPATH, '//*[@class="page"]/a[last()]')))
            print('after wait')
            page += 1
        else:
            break


def active_proxies(url, db, table, table_new):
    proxylst = myClient[db][table].find()
    for i in proxylst:
        try:
            proxy = {}
            header = {'User-Agent': ua['google chrome']}
            proxyHost = i['proxyHost']
            proxyPort = i['proxyPort']
            proxyProtocol = i['proxyProtocol']
            proxyMate = "http://{}:{}".format(proxyHost,proxyPort)
            ips = {
                "http": proxyMate,
                "https": proxyMate
            }
            resp = requests.get(url, header, proxies=ips)
            print(resp)
            if resp.status_code == 200:
                proxy['proxyHost'] = proxyHost
                proxy['proxyPort'] = proxyPort
                proxy['proxyProtocol'] = proxyProtocol
                proxy['test time'] = datetime.now().isoformat()
                proxy['response code'] = '200'
                myClient[db][table_new].insert_one(proxy)
        except OSError as err:
            print("OS error: {0}".format(err))
        except ValueError:
            print("Could not convert data to an integer.")
        except:
            print("Unexpected error:", sys.exc_info())

def get_proxy(db, table):
    proxyInfo = myClient[db][table].find({'response code':200})
    proxyHost = proxyInfo['proxyHost']
    proxyPort = proxyInfo['proxyPort']
    proxyMate = "http://{}:{}".format(proxyHost, proxyPort)
    ips = {
        "http": proxyMate,
        "https": proxyMate
    }
    return ips

if __name__ == '__main__':
    proxies_extractor('ProxyDB')
    active_proxies('https://www.google.com/', 'ProxyDB', 'proxy', 'active_proxy')