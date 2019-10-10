from selenium.common.exceptions import NoSuchElementException
import json
from collections import OrderedDict
from datetime import datetime
from time import sleep
import random
from selenium import webdriver
from datetime import datetime, timedelta


def crawler(driver, meta, db, word):
    '''
    :param meta: { name, cafe_url, last_time: '%Y.%m.%d' }
    '''
    name = meta['name']
    cafe_url = meta['cafe_url']
    last_date = datetime.strptime(meta['last_date'], '%Y.%m.%d')

    driver.implicitly_wait(1)

    base_url = 'https://search.naver.com/search.naver?where=article&query=[q]&ie=utf8&st=rel&date_option=6&date_from=[date]&date_to=[date]&board=&srchby=text&dup_remove=1&cafe_url=[cafeurl]'
    target_date = last_date

    boards = []

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

            if len(boards) > 20:
                # FIXME update last_date to (target_date + timedelta(days=1)).strftime('%Y.%m.%d')
                db.word_table.update_many(boards, upsert=True)
                boards.clear()

            target_date = target_date + timedelta(days=1)

            if target_date > datetime.now():
                if len(boards) > 0:
                    db.word_table.update_many(boards, upsert=True)
                return
    except KeyboardInterrupt:
        # FIXME update last_date to (target_date + timedelta(days=1)).strftime('%Y.%m.%d')
        if len(boards) > 0:
            db.word_table.update_many(boards, upsert=True)