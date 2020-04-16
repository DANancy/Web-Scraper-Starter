import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
import os


def get_cookies(info):
    lines = info.split('; ')
    dic_cookies = {}
    for line in lines:
        dic_cookies[line.split('=')[0]] = line.split('=')[1]
    return dic_cookies


def get_category_urls(base_url, header, cookie):
    categorylst = []
    r = requests.get(url=base_url, headers=header, cookies=cookie)
    soup = BeautifulSoup(r.text, 'lxml')
    categories = soup.select('#p_lt_ctl08_pageplaceholder_p_lt_ctl00_wCM_AMS_tg_tvn0Nodes > table .CategoryTreeItem a')
    # categories=soup.find_all('span',class_='CategoryTreeItem')
    for a in categories:
        categorylst.append("https://www.chemistwarehouse.com.au{}".format(a['href']))
    return categorylst


def get_item_urls(category_url, header, cookie):
    dic_urls = []

    for c in category_url:
        r = requests.get(url=c, headers=header, cookies=cookie)
        # r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, 'lxml')
        page = soup.find('a', class_='last-page')

        dic_urls.append(c)
        if page != None:
            totalpages = int(soup.find('a', class_='last-page')['href'].split('=')[1])
            for i in range(totalpages - 1):
                url = "{}?page={}".format(c, str(i + 2))
                dic_urls.append(url)
    return dic_urls


def get_data(search_url, header, cookie, table):
    print('start {}'.format(search_url))
    r = requests.get(url=search_url, headers=header, cookies=cookie)
    # r.encoding = r.apparent_encoding
    soup = BeautifulSoup(r.text, 'lxml')

    base_url = 'https://www.chemistwarehouse.com.au'
    items = soup.find_all('a', class_='product-container')
    n = 0
    for i in list(items):
        product = {}
        product['URL'] = base_url + i['href']

        skuid = product['URL'].split('/')[4]
        reviewUrl = "https://api.bazaarvoice.com/data/batch.json?passkey=5tt906fltx756rwlt29pls49v&apiversion=5.5&displaycode=13773-en_au&resource.q0=products&filter.q0=id%3Aeq%3A{}&stats.q0=reviews&filteredstats.q0=reviews&filter_reviews.q0=contentlocale%3Aeq%3Aen*%2Cen_AU&filter_reviewcomments.q0=contentlocale%3Aeq%3Aen*%2Cen_AU".format(
            str(skuid), str(skuid))
        r2 = requests.get(reviewUrl).json()
        # r.encoding = r.apparent_encoding
        product['Review'] = round(
            r2['BatchedResults']['q0']['Results'][0]['FilteredReviewStatistics']['AverageOverallRating'], 2)

        product['ID'] = skuid
        product['Title'] = i['title']
        product['Price'] = float(i.find('span', class_='Price').text.split('$')[1].split(' ')[0])
        save = i.find('span', class_='Save')
        if save is None:
            product['Save'] = 0.00
        else:
            product['Save'] = float(save.text.split('$')[1].split(' ')[0])
        product['Insert Time'] = datetime.now().isoformat()
        n += 1
        table.insert_one(product)
    return n


if __name__ == "__main__":
    load_dotenv()

    base_url = 'https://www.chemistwarehouse.com.au/categories'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'}

    cookies = os.getenv('CWCOOKIES')
    cookieslst = get_cookies(cookies)
    categorylst = get_category_urls(base_url, headers, cookieslst)
    urlst = get_item_urls(categorylst, headers, cookieslst)

    myclient = MongoClient(os.getenv("DBCONNECT"))
    db = myclient['test2']
    datatable = db['table05']

    count = 0
    errorlist = []
    for u in urlst:
        try:
            count += get_data(u, headers, cookieslst, datatable)
            print('Save {} items'.format(count))
        except:
            errorlist.append(u)
