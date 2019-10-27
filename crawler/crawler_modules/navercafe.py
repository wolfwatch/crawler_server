from urllib.parse import quote_plus

from selenium.common.exceptions import NoSuchElementException
import json
from collections import OrderedDict
from datetime import datetime
from time import sleep
import random
from selenium import webdriver
from datetime import datetime, timedelta

from pymongo import MongoClient

def crawler(driver, meta, db, word):

    #메타 받아오기
    #:param meta: { site, url, last_date: '%Y.%m.%d' }

    name = meta['site']
    cafe_url = meta['url'].lstrip('https://cafe.naver.com/') #https://cafe.naver.com/dieselmania 이런 주소가 있다면 dieselmania 이 부분만 들어가야함
    print(cafe_url)
    last_date = meta['last_date']
    #last_date = datetime.strptime(meta['last_date'], '%Y.%m.%d') #문자열로 날짜 시간 객체 만들기
    driver.implicitly_wait(1)

    base_url = 'https://search.naver.com/search.naver?where=article&query=[q]&ie=utf8&st=rel&date_option=6&date_from=[date]&date_to=[date]&board=&srchby=text&dup_remove=1&cafe_url=[cafeurl]'
    target_date = last_date

    boards = []
    now = datetime.now()
    try:
        while True:
            target_url = base_url.replace('[q]', word).replace('[date]', target_date.strftime('%Y.%m.%d')).replace('[cafeurl]', cafe_url)

            driver.get(target_url)

            result_count = 0
            try:
                titlenum = driver.find_element_by_class_name('title_num').get_attribute('innerText')
                # titlenum = '1-10 / n건'
                result_count = int(titlenum.split('/')[1].strip()[:-1].replace(',', ''))
            except NoSuchElementException:
                # no search result
                pass

            #print(str(result_count))

            board = OrderedDict()
            board['word'] = word
            board['site'] = name
            board['date'] = target_date
            board['count'] = result_count
            boards.append(board)

            print(len(boards))
            #print("word ", board['word'])
            #print("site ", board['site'])
            #print("date ", board['date'])
            #print("count ", board['count'])

            #현재 result table만 업데이 되는 것
            if len(boards) > 20:
                # FIXME update last_date to (target_date + timedelta(days=1)).strftime('%Y.%m.%d')
                db.result_table.insert_many(boards)
                print("넣었습니다!")
                # db.rawdata.update_one({"site": name}, {"$addToSet": {"board": {"$each": boards}}})
                list_cursor = db.word_table.find({"word": word}, {"_id": 0})
                list = list_cursor[0]["last_info"]


                count = -1
                for item in list :
                    count += 1
                    if name == item["site"] :
                        break
                #last_info의 몇번째 딕셔너리인지 count 한다.
                db.word_table.update_one({"word" : word}, { "$set" : {"last_info." + str(count) +".last_date" : now}})
                #"post_num." + str(i): post_num






            target_date = target_date + timedelta(days=1)
            print("target table : ", str(target_date))
            print("datetime.now :", str(now))

            #종료하기 전에 남아있는 데이터 저장
            if target_date > now:
                if len(boards) > 0:
                    print("마지막으로 넣습니다!")
                    db.result_table.insert_many(boards)

                    #last_date 추가하는 부분
                    count = -1
                    for item in list:
                        count += 1
                        if name == item["site"]:
                            break
                    # last_info의 몇번째 딕셔너리인지 count 한다.
                    db.word_table.update_one({"word": word}, {"$set": {"last_info." + str(count) + ".last_date": now}})
                    # "post_num." + str(i): post_num

                return
    except KeyboardInterrupt: #ctrl_C로 종료할 때 남아있는 데이터 저장
        # FIXME update last_date to (target_date + timedelta(days=1)).strftime('%Y.%m.%d')
        if len(boards) > 0:
            db.result_table.insert_many(boards)

            # last_date 추가하는 부분
            count = -1
            for item in list:
                count += 1
                if name == item["site"]:
                    break
            # last_info의 몇번째 딕셔너리인지 count 한다.
            db.word_table.update_one({"word": word}, {"$set": {"last_info." + str(count) + ".last_date": now}})
            # "post_num." + str(i): post_num


'''
uri = "mongodb://%s:%s@%s" % (quote_plus("admin123"), quote_plus("1234"), "wolfwatch.dlinkddns.com:27017/admin")
client = MongoClient(uri)
# 디비 연결
DB = client.crawler_db

# open chrom
doptions = webdriver.ChromeOptions()
doptions.add_extension('ublock.crx')
doptions.add_extension('blockimage.crx')

dr = webdriver.Chrome('C://driver/chromedriver', options=doptions)

me = OrderedDict()
me["site"] = "디젤매니아"
me["url"] = "https://cafe.naver.com/dieselmania"
me["last_date"] = datetime.strptime('2019-08-19', '%Y-%m-%d')

crawler(dr, me, DB, "차")

'''