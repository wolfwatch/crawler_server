import datetime
import time
from random import randint

from selenium.common.exceptions import NoSuchElementException
import json
from collections import OrderedDict


def crawler(driver, name, url, db, word):
    # todo : change url
    url = 'http://www.inven.co.kr/board/'

    # name : 사이트 이름, ex) inven, instiz
    # word : 검색할 신조어 ex) 아아, 때죽아

    #------ declare ------#
    boards = []

    #------ get all url of sites (inven, instiz, dotax...... ilbe) from json meta file------#
    # use json file or DB
    # cursor = db.rawdata.find({}, {"_id": 0, "site_name": 1, "site_address": 1})
    # site_address = cursor["site_address"]
    # site_name = cursor["site_name"]
    # -> 이건 crawler_format.py에서,
    # 멀티 쓰레드가 구현된 for 안에 있는 crawl()안에
    # 각각의 site url과 이름을  crawl(site_address, site_name) 식으로 넣어서 전달


    #------ wait finding element, for max 5sec ------#
    driver.implicitly_wait(2)

    # get word from crawler_format.py ( views.py )
    # word = "asfsag"

    # get starting date, from Json file or DB
    # roof counting date from 20xx.xx.xx to now(2019.10.07)
    for date in #####:

        # url를 이용해서 driver 접근
        # ex) address에는 "inven.co.kr" 이런 형식의 address가 들어가 있다.

        # set date, increasing number
        date = ''
        # find number of post
        count = ''

        # Ex)
        # word : "실화냐"/ date : "2019.10.07" / site : "inven" / count : 2701
        #------ store data to board[] ------#
        boards = []
        board = OrderedDict()
        board['word'] = word
        board['site'] = name
        board['date'] = datetime.datetime.strptime(date, "%Y-%m-%d")
        board['count'] = count
        boards.append(board)

        # ------ save it every 20 count ------#
        if len(boards) > 20:
            db.raw_table.insert_many(boards)

    db.raw_table.insert_many(boards)
                # save data to json
    # json_string = json.dumps(file_data, ensure_ascii=False, indent="\t")

    return
