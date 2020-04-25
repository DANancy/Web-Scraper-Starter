# import pandas
# print(pandas.__file__)
# save this module to the package folder

# ! /usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from proxy.getProxy import get_proxy


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

    while True:
        proxy = get_proxy('ProxyDB', 'active_proxy')
        if proxy is None:
            break
        r = requests.get(url=search_url, headers=h_dict, cookies=c_dict, proxies=proxy)
        if r == 200:
            r.encoding = r.apparent_encoding
            return r.json()
    raise ValueError('No Available Proxy')
