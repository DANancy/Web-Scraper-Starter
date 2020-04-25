# web-scraper-starter

This is a web scrap project, built on top of Python and Mongodb. 

#### Existing Web Scrapers
1. [Bilibili](https://www.bilibili.com) (completed)
2. [Chemist Warehouse](https://www.chemistwarehouse.com.au) (ongoing)

#### File Strcutre
```
.
├── bilibili                   # Project files for bilibili 
    ├── helper                 # customized molude
    ├── data_extractor         # spider for bilibili
    ├── data_cleaner           # data cleaning on MongoDB
    ├── video_analysis         # dashboard built on Poltly & Dash
    └── api_call_sample.json   # bilibili danmaku api call sample
├── chemist_warehouse          # Project files for Chemist Warehouse
    ├── data_extractor         # spider for chemist warehose
    └── review_sample.json     # product review api call sample
├── images                     # Images for architecture
├── proxy                      # Customized Proxy Pacakge
├── LICENSE
├── .env-sample                # Rename to .env to setup environmental variables
├── .gitignore
├── requirements.txt
└── README.md
```

#### Scraper Architecture Diagram - Bilibili
![Image of Diagram](images/bilibili_scraper_diagram.png)

#### Bilibili Project Setup 
1.Clone the whole project
```
git clone https://github.com/gitnancy/web-scrapter-starter.git
```
2.Install Python Projects
```shell
pip install -r requirements.txt
```
3.Install [MongoDB](https://www.mongodb.com/download-center/enterprise?tck=docs_server) & [Robo 3T](https://robomongo.org/)

4.Create .env File
```
COOKIE: setup cookie info for website login
PASSWORD: setup user password for website login
USERNAME: setup username for website login
DBCONNECT: setup DB Connection
```
5.Setup Proxy DB
```shell
python proxy\proxy_extractor.py
```
6.Run Extractor
```shell
python bilibili\bilibili_data_extractor.py
```
7.Run Cleaner
```shell
python bilibili\bilibili_data_cleaner.py
```
8.Run Dashboard
```shell
python bilibili\video_analysis.py
```
#### Helpful Cheat Sheets & Tools
* [XPATH](https://devhints.io/xpath)
* [REGEX](https://www.debuggex.com/cheatsheet/regex/python)
* [Seleinum Extension for Chrome](https://chrome.google.com/webstore/detail/selenium-ide/mooikfkahbdckldjjndioackbalphokd?hl=en)
* [Search Engine for IoT](https://www.shodan.io/)