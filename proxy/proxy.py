import requests
from bs4 import BeautifulSoup

def get_ursl(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')

    lis = soup.find()
    urlst = []
    for i in list:
        url =
        urlst.append()
    return urlst


def get_proxy():
    proxyHost = "192.168.0.248"
    proxyPort = "1081"

    proxyMate = "http://%(host)s:%(port)s" % {
        "host": proxyHost,
        "port": proxyPort,
    }
    ips = {
        "http": proxyMate,
        "https": proxyMate,
    }
    r=requests.get('http://freeproxylists.net/', proxies=ips)
    print(r.status_code)
get_proxy()