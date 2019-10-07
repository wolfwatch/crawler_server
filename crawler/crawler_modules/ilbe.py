import datetime

from selenium.common.exceptions import NoSuchElementException
import json
from collections import OrderedDict


def crawler(driver, name, db):
    # todo : change url
    url = 'https://www.ilbe.com/list/'

    #------ declare ------#
    boards = []
    file_data = OrderedDict()

    #------ get post_nums & gallery_url ------#
    cursor = db.rawdata.find_one({"site": name}, {"_id": 0, "post_num": 1, "gallery_url": 1})
    gallery_url = cursor["gallery_url"]
    post_nums = cursor["post_num"]

    #------ wait finding element, for max 5sec ------#
    driver.implicitly_wait(2)

    # for : 첫번째 겔러리 ~ n번째 갤러리
    for i in range(0, len(gallery_url)):

        print(url + gallery_url[i])
        # find latest post_number of post, to set max number

        driver.get(url + gallery_url[i])

        max_post_num = driver.find_element_by_css_selector('div.board-list > ul > li:nth-child(6) > span.count').text
        max_post_num = max_post_num.replace(",","")
        print(int(max_post_num))

        #------ check latest ------#
        if post_nums[i] >= int(max_post_num) - 1:
            continue

        n = (int(max_post_num) - post_nums[i]) / 30
        extra = (int(max_post_num) - post_nums[i]) % 30
        print(extra)

        post_num = post_nums[i]
        #page 35      2페이지     2페이지만
        #3개씩 목록 번호를 받아오겠다.
        #6 -> 2        7 -> 2

        # case 1
        # 마지막 번호 : 70, 최신 105
        # list 35 -> 30개만
        # 2page: 70~75, 1page: 75~105
        # 1. 70 ~ 100 ->
        # one page => 70 ~ 100 -> 30개
        # 2. 105 ~ 75

        # case.2
        # 마지막 번호 : 70, 최신 195
        # List 125 -> 120개 만 ->  n=4,  +1
        # 1page 195 ~ 166, 2page 165 ~ 136, 3page 135 ~ 106, 4page 105 ~ 76, 5page 75 ~ 70
        # 1. 70 ~ 190
        # 2. 195 ~ 75
        try_num = int(n)
        addr_list = []
        #새로 갱신된 목록이 많아질 수록 순환 횟수가 늘어난다. 3페이지씩 목록을 가져온다.

        driver.get('http://www.ilbe.com/list/free?page=' + str(try_num+1) + '&listStyle=list')
        q = driver.find_element_by_class_name('board-body')
        w = q.find_elements_by_class_name('subject')
        extra_cnt = 0
        for addr_url in w:
            extra_cnt += 1
            if(extra_cnt > extra):
                break
            addr_list.append(addr_url.get_attribute('href'))

        cnt = 0
        # ------ get each gallery ------#
        for addr in addr_list:
            cnt += 1
            try:
                # ------ get each gallery ------#
                driver.get(addr)

                # parsing html part
                r = driver.find_element_by_class_name('post-header')
                t = r.find_element_by_tag_name('h3')
                title = t.get_attribute('innerText')
                y = driver.find_element_by_class_name('post-count')
                u = y.find_element_by_class_name('date')
                date = datetime.datetime.strptime(u.get_attribute('innerText'), "%Y-%m-%d %H:%M:%S")

                o = driver.find_element_by_class_name('post-content')
                content = o.get_attribute('innerText')

                # ------ store data to board[] ------#
                board = OrderedDict()
                board['title'] = title
                board['date'] = date
                board['url'] = addr
                board['content'] = content
                boards.append(board)
                json_string = json.dumps(boards, ensure_ascii=False, indent="\t")
                print(json_string)

            except NoSuchElementException:
                continue

            # ------ save it every 15 count ------#
            if len(boards) > 15:
                # ------ to update last post_num ------#
                db.rawdata.update_one({"site": name}, {"$set": {"post_num." + str(i): post_num + cnt}})
                # ------ save data to db ------#
                db.rawdata.update_one({"site": name}, {"$addToSet": {"board": {"$each": boards}}})
                # ------ init ------ #
                boards = []
                cnt = 0

        cnt = 0
        while try_num > 0 :
            # 3보다 큰 경우
            if try_num > 3 :
                for m in range(try_num, try_num-3, -1) :
                    driver.get('http://www.ilbe.com/list/free?page=' + str(m) + '&listStyle=list')
                    q = driver.find_element_by_class_name('board-body')
                    w = q.find_elements_by_class_name('subject')
                    for addr_url in w:
                        addr_list.append(addr_url.get_attribute('href'))
            elif try_num <= 3 and try_num > 0: # 3보다 작고 0보다는 큰경우
                for m in range(try_num, 0, -1) :
                    driver.get('http://www.ilbe.com/list/free?page=' + str(m) + '&listStyle=list')
                    q = driver.find_element_by_class_name('board-body')
                    w = q.find_elements_by_class_name('subject')
                    for addr_url in w:
                        addr_list.append(addr_url.get_attribute('href'))

            try_num -= 3
            cnt = 0
            #------ get each gallery ------#
            for addr in addr_list:
                cnt += 1
                try:
                    #------ get each gallery ------#
                    driver.get(addr)

                    # parsing html part
                    r = driver.find_element_by_class_name('post-header')
                    t = r.find_element_by_tag_name('h3')
                    title = t.get_attribute('innerText')
                    y = driver.find_element_by_class_name('post-count')
                    u = y.find_element_by_class_name('date')
                    date = u.get_attribute('innerText')
                    o = driver.find_element_by_class_name('post-content')
                    content = o.get_attribute('innerText')

                    #------ store data to board[] ------#
                    board = OrderedDict()
                    board['title'] = title
                    board['date'] = date
                    board['url'] = addr
                    board['content'] = content
                    boards.append(board)

                    json_string = json.dumps(boards, ensure_ascii=False, indent="\t")
                    print(json_string)

                except NoSuchElementException:
                    continue

                # ------ save it every 15 count ------#
                if len(boards) > 15:
                    # ------ to update last post_num ------#
                    db.rawdata.update_one({"site": name}, {"$set": {"post_num." + str(i): post_num + cnt}})
                    # ------ save data to db ------#
                    db.rawdata.update_one({"site": name}, {"$addToSet": {"board": {"$each": boards}}})
                    # ------ init ------ #
                    boards = []
                    cnt = 0

            # after crawling is done for one gallery
            # ------ to update last post_num ------#
            db.rawdata.update_one({"site": name}, {"$set": {"post_num." + str(i): post_num + cnt}})
            # ------ save data to db ------#
            db.rawdata.update_one({"site": name}, {"$addToSet": {"board": {"$each": boards}}})
            # ------ init ------ #
            boards = []
            addr_list = []
            cnt = 0

    # save data to json
    json_string = json.dumps(file_data, ensure_ascii=False, indent="\t")

    return json_string
