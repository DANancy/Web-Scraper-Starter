# import pandas
# print(pandas.__file__)
# save this module to the package folder

# ! /usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

import requests
from requests.exceptions import ProxyError
import proxy.proxy_manager as PM

def get_cookies(input):
    dic = {}
    cookies = input.split('; ')
    for c in cookies:
        dic[c.split('=')[0]] = c.split('=')[1]
    return dic


def api_call(page, starttime, endtime, h_dict, c_dict):
    # https://s.search.bilibili.com/cate/search?callback=jqueryCallback_bili_7977332783896514&main_ver=v3&search_type=video&view_type=hot_rank&order=click&copy_right=-1&cate_id=24&page=1&pagesize=20&time_from=20200408&time_to=20200415&_=1586958278647

    search_url = "https://s.search.bilibili.com/cate/search?callback=jqueryCallback_bili_7977332783896514&main_ver=v3&search_type=video&view_type=hot_rank&order=click&copy_right=-1&cate_id=24&page={}&pagesize=2&time_from={}&time_to={}".format(
        page, starttime, endtime)

    r = proxy_call(search_url, h_dict, c_dict)
    return r.json()

def proxy_call(url,h_dict,c_dict):
    while True:
        try:
            r = requests.get(url=url, headers=h_dict, cookies=c_dict, proxies=PM.myProxy.get_proxy())
            if r.status_code == 200:
                return r
            else:
                print("Invalid Proxy: {}".format(r.status_code))
                PM.myProxy.invalid_proxy()
        except ProxyError:
            PM.myProxy.invalid_proxy()