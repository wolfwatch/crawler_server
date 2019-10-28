from selenium.common.exceptions import NoSuchElementException

from collections import OrderedDict
import time
from random import randint
from datetime import datetime, timedelta
from selenium.webdriver.common.keys import Keys

def crawler(driver, meta, db, word):
    '''
    :param meta: { name, url, extra_query, last_date: '%m/%d/%Y' }
    '''
    name = meta['site']
    site_url = meta['url']
    extra_query = meta['extra_query']
    target_date = meta['last_date']

    driver.implicitly_wait(1)

    query = word + ' and \"' + extra_query+'\" site:' + site_url # + ' ' + extra_query

    base_url = 'https://www.google.com/search?q=[q]&tbs=li:1%3A1%2Ccd_min%3A[month]%2F[day]%2F[year]%2Ccd_max%3A[month]%2F[day]%2F[year]'
    # https://www.google.com/search?q=[q]&tbs=cdr%3A1%2Ccd_min%3A[month]%2F[day]%2F[year]%2Ccd_max%3A[month]%2F[day]%2F[year]

    boards = []
    now = datetime.now()
    login(driver)
    try:
        while True:
            target_url = base_url.replace('[q]', query).replace('[month]', target_date.strftime('%m')).replace('[day]', target_date.strftime('%d')).replace('[year]', target_date.strftime('%Y'))
            driver.get(target_url)
            result_count = 0
            try:
                # block 방지
                rand_value = randint(1, 50)
                time.sleep(rand_value / 50)
                resultstats = driver.find_element_by_id('resultStats').get_attribute('innerText')
                if '약' in resultstats:
                    # resultstats = '검색결과 n,nnn개 (n초)'
                    result_count = int(resultstats.split(' ')[2][:-1].replace(',', ''))
                else:
                    # resultstats = '검색결과 약 n,nnn개 (n초)'
                    result_count = int(resultstats.split(' ')[1][:-1].replace(',', ''))
            except NoSuchElementException:
                try:
                    driver.switch_to.frame(
                        driver.find_element_by_xpath('//div[@id="recaptcha"]/div[1]/div[1]/iframe[1]'))
                    check = driver.find_element_by_xpath('//span[@id="recaptcha-anchor"]')
                    time.sleep(2)
                    check.click()
                    print("클릭함.")
                    time.sleep(2)
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
                db.result_table.insert_many(boards)
                print("넣었습니다!")
                update_last(name, word, db, target_date)
                boards = []

            target_date = target_date + timedelta(days=1)

            if target_date > now:
                if len(boards) > 0:
                    db.result_table.insert_many(boards)
                    update_last(name, word, db, target_date)
                return
    except KeyboardInterrupt:  # Ctrl-C
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

def login(driver):
    target_url = "https://www.google.com/"
    driver.get(target_url)
    driver.find_element_by_id('gb_70').click()
    # time.sleep(700)
    driver.find_element_by_name('identifier').send_keys('wolfwatch93')
    driver.find_element_by_xpath('//*[@id="identifierNext"]/span[1]/span[1]').click()
    time.sleep(3)
    driver.find_element_by_name('password').send_keys('')
    driver.find_element_by_xpath('//*[@id="passwordNext"]').send_keys(Keys.ENTER)
    time.sleep(3)