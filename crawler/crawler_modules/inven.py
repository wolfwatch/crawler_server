import datetime
import time
from random import randint

from selenium.common.exceptions import NoSuchElementException
import json
from collections import OrderedDict

def crawler(driver, name, db):
    # main address of inven
    url = 'http://www.inven.co.kr/board/'

    # declare
    boards = []
    file_data = OrderedDict()

    cursor = db.rawdata.find_one({"site": name}, {"_id": 0, "post_num": 1, "gallery_url": 1})
    gallery_url = cursor["gallery_url"]
    post_nums = cursor["post_num"]
    file_data["gallery_url"] = gallery_url
    file_data["post_num"] = post_nums

    # wait finding element, for max 5sec
    driver.implicitly_wait(2)

    # for : 첫번째 겔러리 ~ n번째 갤러리
    for i in range(0, len(gallery_url)):

        # find latest post_number of post, to set max number
        driver.get(url + gallery_url[i])
        max_post_num = driver.find_element_by_xpath('//tr[@class="ls tr tr2"][1]/td[1]').text
        print(int(max_post_num))

        # check latest
        if post_nums[i] >= int(max_post_num) - 1:
            continue

        post_num = post_nums[i]
        for post_num in range(post_nums[i], int(max_post_num)):
            # block 방지
            rand_value = randint(1, 3)
            time.sleep(rand_value)
            try:
                # get each gallery
                driver.get(url + gallery_url[i] + str(post_num))

                title = driver.find_element_by_xpath('//*[@class="articleTitle"]/h1[1]').text
                date = driver.find_element_by_xpath('//*[@class="articleDate"]').text
                content = driver.find_element_by_xpath('//*[@id="powerbbsContent"]').text

                board = OrderedDict()
                board['title'] = title
                board['date'] = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M")
                board['url'] = url + gallery_url[i] + str(post_num)
                board['content'] = content
                boards.append(board)



            except NoSuchElementException:
                try:
                    # check is_board
                    driver.find_element_by_xpath('//*[@id="comFloatAlert"]')
                    print("no post")
                except NoSuchElementException:
                    try:
                        # check is_board
                        temp = driver.find_element_by_xpath('//*[@class="articleTitle"]/h1[1]').text
                        continue
                    except NoSuchElementException:
                        print("no response")
                        break

            if len(boards) > 20:
                # ------ save it every 20 count ------#
                # ------ to update last post_num ------#
                db.rawdata.update_one({"site": name}, {"$set": {"post_num." + str(i): post_num}})
                # ------ save data to db ------#
                db.rawdata.update_one({"site": name}, {"$addToSet": {"board": {"$each": boards}}})
                # ------ init ------ #
                boards = []

        # after crawling is done for one gallery
        # ------ to update last post_num ------#
        db.rawdata.update_one({"site": name}, {"$set": {"post_num." + str(i): post_num}})
        # ------ save data to db ------#
        db.rawdata.update_one({"site": name}, {"$addToSet": {"board": {"$each": boards}}})
        # ------ init ------ #
        boards = []

    file_data["site"] = name
    file_data["board"] = []
    # save data to json


    # save data to json
    json_string = json.dumps(file_data, ensure_ascii=False, indent="\t")

    return json_string
