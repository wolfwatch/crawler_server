import datetime
import time
from random import randint

from selenium.common.exceptions import NoSuchElementException, UnexpectedAlertPresentException
import json
from collections import OrderedDict


def crawler(driver, name, db):
    # main address of inven
    url = 'https://pann.nate.com/'

    # declare
    boards = []
    file_data = OrderedDict()

    # check pre_data
    cursor = db.rawdata.find_one({"site": name}, {"_id": 0, "post_num": 1, "gallery_url": 1})
    gallery_url = cursor["gallery_url"]
    post_nums = cursor["post_num"]
    file_data["gallery_url"] = gallery_url
    file_data["post_num"] = post_nums

    # wait finding element, for max 5sec
    driver.implicitly_wait(3)

    # find latest post_number of post, to set max number
    driver.get(url + gallery_url[0] + 'c20001')
    latest_post = driver.find_element_by_xpath('//tr[@class="first"]/td[1]/a[1]').get_attribute('href')

    max_post_num = latest_post.replace('https://pann.nate.com/talk/', '').replace('?page=1', '')
    print(max_post_num)

    # check latest
    if post_nums[0] < int(max_post_num) - 1:

        post_num = post_nums[0]
        for post_num in range(post_nums[0], int(max_post_num)):
            # block 방지
            rand_value = randint(1, 3)
            time.sleep(rand_value)
            try:
                # get each gallery
                driver.get(url + gallery_url[0] + str(post_num))
                title = driver.find_element_by_xpath('//div[@class="view-wrap"]/div[1]/h4[1]').get_attribute('title')
                date = driver.find_element_by_xpath('//span[@class="date"]').text
                content = driver.find_element_by_xpath('//div[@id="contentArea"]').text

                board = OrderedDict()
                board['title'] = title
                board['date'] = datetime.datetime.strptime(date, "%Y.%m.%d %H:%M")
                board['url'] = url + gallery_url[0] + str(post_num)
                board['content'] = content
                boards.append(board)
                print(content)
            except UnexpectedAlertPresentException:
                print("no post")
            # except selenium.common.exceptions.WebDriverException:
                #print("no post")
            except NoSuchElementException:
                try:
                    content = driver.find_element_by_xpath('//*[@id="contentArea"]/p[1]').text
                    board['content'] = content
                    boards.append(board)
                    print(content)
                except UnexpectedAlertPresentException:
                    try:
                        # check is_board
                        driver.find_element_by_xpath('//*[@class="topalert"]')
                        print("no post")
                    except NoSuchElementException:
                        print("no response")
                        break

            if len(boards) > 20:
                # ------ save it every 20 count ------#
                # ------ to update last post_num ------#
                db.rawdata.update_one({"site": name}, {"$set": {"post_num." + str(0): post_num}})
                # ------ save data to db ------#
                db.rawdata.update_one({"site": name}, {"$addToSet": {"board": {"$each": boards}}})
                # ------ init ------ #
                boards = []

        # after crawling is done for one gallery
        # ------ to update last post_num ------#
        db.rawdata.update_one({"site": name}, {"$set": {"post_num." + str(0): post_num}})
        # ------ save data to db ------#
        db.rawdata.update_one({"site": name}, {"$addToSet": {"board": {"$each": boards}}})

        file_data["site"] = name
        file_data["board"] = []
        # save data to json
    json_string = json.dumps(file_data, ensure_ascii=False, indent="\t")

    return json_string
