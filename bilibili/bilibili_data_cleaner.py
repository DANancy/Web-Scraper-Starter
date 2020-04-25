#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient
import os
from dotenv import load_dotenv
from pathlib import Path
import pandas as pd
from datetime import datetime
import time

def data_extract(table):
    data = pd.DataFrame(list(table.find()))
    return data


def data_cleaning_infos(table_from, table_to):
    old_data = data_extract(table_from)

    timestart = time.time()
    del old_data['_id']
    old_data['tag']=old_data['tag'].str.split(',')
    old_data['play'] = old_data['play'].astype('int')
    old_data['cleaned Time'] = datetime.now().isoformat()
    new_data = old_data.to_dict(orient='records')
    timeend = time.time()
    table_to.insert_many(new_data)
    print('cleaning infos is %.2fs' % (timeend - timestart))


def data_cleaning_details(table_from, table_to):
    old_data = data_extract(table_from)

    timestart = time.time()
    del old_data['_id']
    old_data['cleaned Time'] = datetime.now().isoformat()
    new_data = old_data.to_dict(orient='records')
    table_to.insert_many(new_data)
    timeend = time.time()
    print('cleaning details is %.2fs' % (timeend - timestart))


if __name__ == "__main__":
    env_path = Path('..') / '.env'
    load_dotenv(dotenv_path=env_path)

    myClient = MongoClient(os.getenv("DBCONNECT"))
    db = myClient['bilibili']

    infostable = db['infos']
    infostable_new = db['infos_new']
    infostable_new.delete_many({})
    data_cleaning_infos(infostable, infostable_new)

    detailstable = db['details']
    detailstable_new = db['details_new']
    detailstable_new.delete_many({})
    data_cleaning_details(detailstable, detailstable_new)
