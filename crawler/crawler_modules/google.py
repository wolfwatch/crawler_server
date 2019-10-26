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

    # 1. Meta Data 받아오기 -> 임시 데이터 생성해서 테스트
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

            # 20개씩 모아서 한번에 저장함.
            if len(boards) > 20:
                # 2. Board를 result 테이블에 업데이트 해주기
                # 3. 워드 테이블의 Last_date 업데이트 해주기 -> 직접 워드 테이블에 접근해줘야함
                # FIXME update last_date to (target_date + timedelta(days=1)).strftime('%m/%d/%Y')
                db.result_table.update_many(boards, upsert=True)
                boards.clear()

            # 날짜 늘려줌
            target_date = target_date + timedelta(days=1)

            # todo: Error check
            # datetime.now() : 초 단위?, 계속 갱신?
            # 1. 단위 비교 -> print(str(   ))
            # 2. datetime.now() -> 시작할 때 변수로 저장
            if target_date > datetime.now():
                # 종료하기전에, 남아있는 데이터 저장
                if len(boards) > 0:
                    db.word_table.update_many(boards, upsert=True)
                return

    except KeyboardInterrupt:  # Ctrl-C로 종료 할 때 -> 남아있는 데이터 저장
        # FIXME update last_date to (target_date + timedelta(days=1)).strftime('%m/%d/%Y')
        db.word_table.update_many(boards, upsert=True)


# 1. 워드 테이블, 스키마 format 만들기 -> word_table_sample.json 이름으로 /data 폴더 아래에 넣어주기
#  => 메뉴얼용 format 파일만들어 달라는 뜻
# 2. 각각의 site_table 만들기
# 3. 검색 엔진별, 사이트 리스트, url 조사
# 4. 2,3번 Mongo에 바로 적용
# 5. 1.번도  mongod에 적용시켜보기
# 네이버랑, 다음 먼저
# 구글을 좀 생각을 해봐야 할듯
