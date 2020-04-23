# web-scraper-starter

This is a web scrap project, built on top of Python and Mongodb. 

#### Existing Web Scrapers
1. [Bilibili](https://www.bilibili.com) (completed)
2. [Chemist Warehouse](https://www.chemistwarehouse.com.au) (ongoing)

#### Scraper Architecture Diagram - Bilibili
![Image of Diagram](images/bilibili_web_scraper_diagram.png)

#### Setup 
1.Clone the whole project
```
git clone https://github.com/gitnancy/web-scrapter-starter.git
```
2.Install Python Projects
```shell
pip install -r requirements.txt
```
3.Install MongoDB: 

https://www.mongodb.com/download-center/enterprise?tck=docs_server

4.Create .env File
```
CWCOOKIE: setup cookie info for website login
CWPASSWORD: setup user password for website login
CWUSERNAME: setup username for website login
DBCONNECT: setup database IP for connection
```
5.Run Extactor
```shell
python bilibili_data_extractor.py
```
6.Run Cleaner
```shell
python bilibili_data_cleaner.py
```
7.Run Dashboard
```shell
python video_analysis.py
```