from selenium.common.exceptions import NoSuchElementException
import json
from collections import OrderedDict
import time
from datetime import datetime, timedelta
from random import randint


def crawler(driver, meta, db, word):
    '''
    :param meta: { name, cafe_url, last_time: '%Y.%m.%d' }
    '''
    name = meta['site']
    cafe_url = meta['url']
    target_date = meta['last_date']

    driver.implicitly_wait(1)

    # get cafe grpid
    driver.get('http://cafe.daum.net/' + cafe_url)
    # http://cafe.daum.net/subdued20club
    grpid = driver.find_element_by_id('down').get_attribute('src').split('=')[1] #[-4:]
    base_url = 'http://cafe.daum.net/_c21_/cafesearch?grpid=' + grpid + '&listnum=20&item=subject&query=[q]&viewtype=all&searchPeriod=[date]-[date]'

    boards = []
    now = datetime.now()
    try:
        while True:
            rand_value = randint(1, 50)
            time.sleep(rand_value / 100)
            target_url = base_url.replace('[q]', word).replace('[date]', target_date.strftime('%Y.%m.%d'))
            driver.get(target_url)
            result_count = 0
            try:
                result_count = int(driver.find_element_by_class_name('search_result_box').find_elements_by_class_name('txt_point')[1].get_attribute('innerText'))
            except:
                # no search result
                pass

            board = OrderedDict()
            board['word'] = word
            board['site'] = name
            board['date'] = target_date
            board['count'] = result_count
            boards.append(board)

            if len(boards) > 20:
                db.result_table.insert_many(boards)
                print("넣었습니다!")
                update_last(name, word, db, target_date)
                boards = []

            target_date = target_date + timedelta(days=1)

            if target_date > now:
                if len(boards) > 0:
                    print("마지막으로 넣습니다!")
                    db.result_table.insert_many(boards)
                    # last_date 추가하는 부분
                    update_last(name, word, db, target_date)
                return
    except KeyboardInterrupt:
        if len(boards) > 0:
            db.result_table.insert_many(boards)
            update_last(name, word, db, target_date)

def update_last(name, word, db, target_date):
    list_cursor = db.word_table.find({"word": word}, {"_id": 0})
    list = list_cursor[0]["last_info"]
    count = -1
    for item in list:
        count += 1
        if name == item["site"]:
            break
    db.word_table.update_one({"word": word}, {"$set": {"last_info." + str(count) + ".last_date": target_date}})

