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
    :param meta: { name, url, extra_query, last_date: '%m/%d/%Y' }
    '''
    name = meta['name']
    site_url = meta['url']
    extra_query = meta['extra_query']
    last_date = datetime.strptime(meta['last_date'], '%m/%d/%Y')

    driver.implicitly_wait(1)

    query = word + ' site:' + site_url + ' ' + extra_query

    base_url = 'https://www.google.com/search?q=[q]&tbs=cdr%3A1%2Ccd_min%3A[month]%2F[day]%2F[year]%2Ccd_max%3A[month]%2F[day]%2F[year]'
    target_date = last_date

    boards = []

    try:
        while True:
            target_url = base_url.replace('[q]', query).replace('[month]', target_date.strftime('%m')).replace('[day]', target_date.strftime('%d')).replace('[year]', target_date.strftime('%Y'))

            driver.get(target_url)

            result_count = 0
            try:
                resultstats = driver.find_element_by_id('resultStats').get_attribute('innerText')
                if '약' in resultstats:
                    # resultstats = '검색결과 n,nnn개 (n초)'
                    result_count = int(resultstats.split(' ')[2][:-1].replace(',', ''))
                else:
                    # resultstats = '검색결과 약 n,nnn개 (n초)'
                    result_count = int(resultstats.split(' ')[1][:-1].replace(',', ''))
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
                # FIXME update last_date to (target_date + timedelta(days=1)).strftime('%m/%d/%Y')
                db.raw_table.update_many(boards, upsert=True)
                boards.clear()

            target_date = target_date + timedelta(days=1)

            if target_date > datetime.now():
                if len(boards) > 0:
                    db.raw_table.update_many(boards, upsert=True)
                return
    except KeyboardInterrupt:  # Ctrl-C
        # FIXME update last_date to (target_date + timedelta(days=1)).strftime('%m/%d/%Y')
        db.raw_table.update_many(boards, upsert=True)
