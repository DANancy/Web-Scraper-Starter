import sys
import requests
from bs4 import BeautifulSoup
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


def get_urls(url, h_dic, c_dic):
    urllst = []
    r = requests.get(url=url, headers=h_dic, cookies=c_dic)
    soup = BeautifulSoup(r.text, 'lxml')

    urls = soup.find_all('li', class_='video-item matrix')
    for u in urls:
        url = "https:{}".format(u.a['href'])
        urllst.append(url)
    return urllst


def get_data(url, h_dic, c_dic, table):
    r = requests.get(url=url, headers=h_dic, cookies=c_dic)
    r.encoding = r.apparent_encoding
    soup = BeautifulSoup(r.text, 'lxml')

    name = soup.find('h1')['title']
    categories = soup.find('span', class_='a-crumbs').find_all('a')
    category = ""
    for c in categories:
        category += "/{}".format(c.text)
    date = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", soup.find('div', class_='video-data').text).group(1)
    cid = re.search(r'"cid":(\d*)', r.text).group(1)

    danmaku_url = "https://comment.bilibili.com/{}.xml".format(cid)
    r2 = requests.get(danmaku_url)
    r2.encoding = r2.apparent_encoding

    n = 0
    items = re.findall(r'<d p=.*?</d>', r2.text)
    for i in items:
        infos = {}
        infos['name'] = name
        infos['category'] = category
        infos['date'] = datetime.strptime(date + ':+0800', '%Y-%m-%d %H:%M:%S:%z')
        infos['cid'] = cid
        infos['comment'] = re.search(r'>(.*)</d>', i).group(1)
        infos['other info'] = re.search(r'<d p="(.*)"', i).group(1)
        infos['Insert Time'] = datetime.now().isoformat()
        table.insert_one(infos)
        n += 1
    return n


if __name__ == "__main__":
    load_dotenv()

    url = "https://search.bilibili.com/all?keyword=%E8%94%A1%E5%BE%90%E5%9D%A4"
    h_dic = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36'}
    cookies = os.getenv('BILICOOKIES')
    c_dic = get_cookies(cookies)
    urls = get_urls(url, h_dic, c_dic)

    myClient = MongoClient(os.getenv("DBCONNECT"))
    db = myClient['bilibili']
    table = db['table01']

    for u in urls:
        start_time = time.time()
        try:
            count = 0
            count += get_data(u, h_dic, c_dic, table)
            print("Insert {} Items with {} seconds".format(count, time.time() - start_time))
        except OSError as err:
            print("OS error: {0}".format(err))
        except ValueError:
            print("Could not convert data to an integer.")
        except:
            print("Unexpected error:", sys.exc_info()[0])
