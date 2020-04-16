import sys
import requests
import re
from pymongo import MongoClient
from datetime import datetime
import time
from dotenv import load_dotenv
import os


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

    r = requests.get(url=search_url, headers=h_dict, cookies=c_dict)
    r.encoding = r.apparent_encoding
    r = r.json()
    return r


def get_urls(starttime, endtime, h_dict, c_dict):
    pageNum = 1
    urllst = []
    testTotal = 20
    while True:
        r = api_call(pageNum, starttime, endtime, h_dict, c_dict)
        totalPages = r['numPages']
        pageSize = r['pagesize']

        for j in range(pageSize):
            url = r['result'][j]['arcurl']
            urllst.append(url)
        if (pageNum < min(totalPages, testTotal)):
            pageNum += 1
        else:
            break
    return urllst


def get_info(starttime, endtime, h_dict, c_dict, table):
    pageNum = 1
    testTotal = 20
    while True:
        r = api_call(pageNum, starttime, endtime, h_dict, c_dict)
        totalPages = r['numPages']
        pageSize = r['pagesize']
        n = 0
        for j in range(pageSize):
            infos = {}
            infos['url'] = r['result'][j]['arcurl']
            infos['title'] = r['result'][j]['title']
            infos['video_id'] = r['result'][j]['id']
            infos['type'] = r['result'][j]['type']
            infos['tag'] = r['result'][j]['tag']
            infos['video_review'] = r['result'][j]['video_review']
            infos['is_pay'] = r['result'][j]['is_pay']
            infos['description'] = r['result'][j]['description']
            infos['play'] = r['result'][j]['play']
            infos['favorites'] = r['result'][j]['favorites']
            infos['rank_score'] = r['result'][j]['rank_score']
            infos['duration'] = r['result'][j]['duration']
            infos['pubdate'] = datetime.strptime(r['result'][j]['pubdate'] + ':+0800',
                                                 '%Y-%m-%d %H:%M:%S:%z').isoformat()
            infos['author'] = r['result'][j]['author']
            infos['insert time'] = datetime.now().isoformat()
            print(infos)
            n += 1
            table.insert_one(infos)

        if (pageNum < min(totalPages, testTotal)):
            pageNum += 1
        else:
            break
    return n


def get_danmaku(search_url, h_dict, c_dict, table):
    r = requests.get(url=search_url, headers=h_dict, cookies=c_dict)
    r.encoding = r.apparent_encoding
    cid = re.search(r'"cid":(\d*)', r.text).group(1)
    danmaku_url = "https://comment.bilibili.com/{}.xml".format(cid)

    r2 = requests.get(danmaku_url)
    r2.encoding = r2.apparent_encoding
    n = 0
    items = re.findall(r'<d p=.*?</d>', r2.text)
    for i in items:
        details = {}
        details['video_id'] = re.search(r'av(\d.*)', search_url).group(1)
        details['cid'] = cid
        details['comment'] = re.search(r'>(.*)</d>', i).group(1)
        details['other info'] = re.search(r'<d p="(.*)"', i).group(1)
        details['Insert Time'] = datetime.now().isoformat()
        print(details)
        table.insert_one(details)
        n += 1
    return n


if __name__ == "__main__":
    load_dotenv()

    starttime = input("Start Time: ")
    endtime = input("End Time: ")

    url = "https://www.bilibili.com/v/douga/mad/?spm_id_from=333.5.b_646f7567615f6d6164.38#/all/click/0/1"
    h_dict = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36'}
    cookies = os.getenv('BILICOOKIES')

    c_dict = get_cookies(cookies)

    myClient = MongoClient(os.getenv("DBCONNECT"))
    db = myClient['bilibili']
    table_infos = db['infos']
    table_details = db['details']

    urls = get_urls(starttime, endtime, h_dict, c_dict)

    try:
        timestart = time.time()
        count = 0
        count += get_info(starttime, endtime, h_dict, c_dict, table_infos)
        print("Insert {} videos with {} seconds ".format(count, (time.time() - timestart)))
    except OSError as err:
        print("OS error: {0}".format(err))
    except ValueError:
        print("Could not convert data to an integer.")
    except:
        print("Unexpected error:", sys.exc_info())

    for u in urls:
        try:
            timestart = time.time()
            count = 0
            count += get_danmaku(u, h_dict, c_dict, table_details)
            print("Insert {} danmakus with {} seconds ".format(count, (time.time() - timestart)))
        except OSError as err:
            print("OS error: {0}".format(err))
        except ValueError:
            print("Could not convert data to an integer.")
        except:
            print("Unexpected error:", sys.exc_info())
