import datetime
import traceback
import json
from threading import Thread

from pymongo import MongoClient
from urllib.parse import quote_plus
from selenium import webdriver
from crawler.crawler_modules import inven, instiz, pann, google, navercafe, daumcafe
from collections import OrderedDict


def end_crawling(json_string, name):

    f = open('data/'+name+'.json', 'w', encoding="utf-8")
    f.write(json_string)

    return f.close()


def set_last_info(cursor, result, engine):
    for site_name in cursor:
        info_list = OrderedDict()
        info_list["site"] = site_name["site"]
        info_list["engine"] = engine
        info_list["last_date"] = datetime.datetime.strptime("2017/06/01", "%Y/%m/%d")
        result.append(info_list)


def check_new_word(db, name):
    try:
        cursor = db.word_table.find({"word": name}, {"_id": 0})
        list = cursor[0]["last_info"]
        print("already exist, it will be updated instead")
    except IndexError:
        print("it's new one, store init word table to db")
        init = OrderedDict()
        init['word'] = name
        init['last_info'] = []

        # set init['last_info'], using data about site list from site table
        g_list_cursor = db.gsite_table.find({}, {"_id":0, "site": 1})
        # set_last_info(g_list_cursor, init['last_info'], "google")

        naver_cursor = db.naver_site_table.find({}, {"_id": 0, "site": 1})
        set_last_info(naver_cursor, init['last_info'], "naver")

        daum_cursor = db.daum_site_table.find({}, {"_id": 0, "site": 1})
        set_last_info(daum_cursor, init['last_info'], "daum")

        # insert init data to word_table
        db.word_table.insert_one(init)


def test_mongo():

    # 몽고DB연동
    try:
        # client = MongoClient("localhost:27017")
        # client = MongoClient("admin123:1234@wolfwatch.dlinkddns.com:27017/admin")
        uri = "mongodb://%s:%s@%s" % (quote_plus("admin123"), quote_plus("1234"), "wolfwatch.dlinkddns.com:27017/admin")
        client = MongoClient(uri)
        # 디비 연결
        db = client.crawler_db

        # 1. input word name
        word = input('크롤링 할 단어를 입력하세요 : ')
        check_new_word(db, word)

        # 워드테이블에서, 해당 워드를 어떤 사이트, 엔진을 이용해서 크롤링 할지 정보를 확인한다
        list_cursor = db.word_table.find({"word": word}, {"_id": 0})
        list = list_cursor[0]["last_info"]

        threads = []
        for item in list:
            meta = OrderedDict()
            # 4. 워드테이블에서 engine 정보 읽고서 -> switch로 엔진에 맞는 크롤러 호출
            # 6. 크롤러 호출을 멀티로 구현 -> site별로 각 엔진에 맞는 크롤러를 수행 할 것임
            if item["engine"] == "google":
                # 2. 워드테이블의 site 이름 -> 사이트테이블의 site를 조회해서, 사이트 테이블에서 url, extra_qyery 가져온다.
                site_cursor = db.gsite_table.find({"site": item["site"]}, {"_id": 0, "site_url": 1, "extra_query": 1})
                meta["extra_query"] = site_cursor[0]["extra_query"]
            elif item["engine"] == "naver":
                site_cursor = db.naver_site_table.find({"site": item["site"]}, {"_id": 0, "url": 1})
            elif item["engine"] == "daum":
                site_cursor = db.daum_site_table.find({"site": item["site"]}, {"_id": 0, "url": 1})

            # 1. list에서 last_info를 읽음 -> site와 last_date를 Meta[]에 넣음
            meta["site"] = item["site"]
            meta["last_date"] = item["last_date"]
            # 3. Meta[]에 url, extra_query를 넣는다.
            print(item["engine"])
            meta["url"] = site_cursor[0]["url"]

            print("site : "+item["site"] + " / url : "+meta["url"])

            # 5. 크롤러 호출 할때 Meta[]와 word 정보 넣어줌
            th_one = Thread(target=crawler, args=(item["engine"], meta, db, word, ))
            th_one.start()
            threads.append(th_one)
            # meta.clear()

            # 동시에 돌릴 쓰레드의 숫자 n
            n = 2
            if len(threads) >= n:
                for t in threads:
                    t.join()

        # Thread t가 종료될 때까지 기다리기
        for t in threads:
            t.join()

    except:
        traceback.print_exc()


def crawler(name, meta, db, word):
    # open chrom
    doptions = webdriver.ChromeOptions()
    doptions.add_extension('ublock.crx')
    doptions.add_extension('blockimage.crx')
    # moved this into if % elif,
    # driver = webdriver.Chrome('C://driver/chromedriver', options=doptions)

    # Each 'site' has a crawler 'module'
    if name == 'google':
        driver = webdriver.Chrome('C://driver/chromedriver', options=doptions)
        google.crawler(driver, meta, db, word)
    elif name == 'naver':
        driver = webdriver.Chrome('C://driver/chromedriver', options=doptions)
        navercafe.crawler(driver, meta, db, word)
    elif name == 'daum':
        driver = webdriver.Chrome('C://driver/chromedriver', options=doptions)
        daumcafe.crawler(driver, meta, db, word)
    else :
        return

    driver.close()
    return


test_mongo()













