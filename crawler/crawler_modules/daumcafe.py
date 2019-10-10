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

    # get cafe grpid
    driver.get('http://cafe.daum.net/' + cafe_url)
    grpid = driver.find_element_by_id('down').get_attribute('src')[-4:]

    base_url = 'http://cafe.daum.net/_c21_/cafesearch?grpid=' + grpid + '&listnum=20&item=subject&query=[q]&viewtype=all&searchPeriod=[date]-[date]'

    target_date = last_date

    boards = []

    try:
        while True:
            target_url = base_url.replace('[q]', word).replace('[date]', target_date.strftime('%Y.%m.%d'))

            driver.get(target_url)

            result_count = 0
            try:
                result_count = int(driver.find_element_by_class_name('search_result_box').find_elements_by_class_name('txt_point')[1].get_attribute('innerText'))
            except:
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
                db.raw_table.update_many(boards, upsert=True)
                boards.clear()

            target_date = target_date + timedelta(days=1)

            if target_date > datetime.now():
                if len(boards) > 0:
                    db.raw_table.update_many(boards, upsert=True)
                return
    except KeyboardInterrupt:
        # FIXME update last_date to (target_date + timedelta(days=1)).strftime('%Y.%m.%d')
        if len(boards) > 0:
            db.raw_table.update_many(boards, upsert=True)