from selenium.common.exceptions import NoSuchElementException
import json
from collections import OrderedDict
from datetime import datetime
from time import sleep
import random

def crawler(driver, name, db):
    # all dc crawler can use same function
    # use separate db entry for gallery separation
    url = 'http://gall.dcinside.com/'

    #------ declare ------#
    boards = []
    file_data = OrderedDict()

    #------ get post_nums & gallery_url ------#
    cursor = db.rawdata.find_one({"site": name}, {"_id": 0, "post_num": 1, "gallery_url": 1})
    gallery_url = cursor["gallery_url"]
    post_nums = cursor["post_num"]

    #------ wait finding element, for max 5sec ------#
    #driver.implicitly_wait(2)

    # for : 첫번째 겔러리 ~ n번째 갤러리
    for i in range(0, len(gallery_url)):

        print(url + gallery_url[i])
        # find latest post_number of post, to set max number
        driver.get(url + gallery_url[i])
        max_post_num = 0
        pn = driver.find_elements_by_class_name('gall_num')
        for j in pn:
            if j.text.isdigit() and int(j.text) > max_post_num:
                max_post_num = int(j.text)
        print(int(max_post_num))
        #post_nums[i] = max_post_num - 10

        #------ check latest ------#
        if post_nums[i] >= int(max_post_num) - 1:
            continue

        post_num = post_nums[i]
        for post_num in range(post_nums[i], int(max_post_num)):
            sleep(random.uniform(1.25, 4))
            try:
                #------ get each gallery ------#
                driver.get(url + gallery_url[i] + str(post_num))

                # parsing html part
                title = driver.find_element_by_class_name('title_subject').text
                date = driver.find_element_by_class_name('gall_date').get_attribute('title')
                content = driver.find_element_by_class_name('writing_view_box').text

                #------ store data to board[] ------#
                board = OrderedDict()
                board['title'] = title
                board['date'] = datetime.strptime(date, '%Y.%m.%d %H:%M:%S')
                board['url'] = url + gallery_url[i] + str(post_num)
                board['content'] = content
                boards.append(board)

                #json_string = json.dumps(boards, ensure_ascii=False, indent="\t")
                #print(json_string)

            except NoSuchElementException:
                '''
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
                '''
                continue

            #------ save it every 20 count ------#
            if len(boards) > 20:
                # ------ save data to db ------#
                # ------ to update last post_num ------#
                post_nums[i] = post_num
                # todo : save psotnum for each gallery
                db.rawdata.update_one({"site": name}, {"$set": {"post_num."+str(i): post_nums[i]}})
                db.rawdata.update_one({"site": name}, {"$addToSet": {"board": {"$each": boards}}})

                # save data in local for checking data
                #file_data["board"] += boards

                #init
                boards = []

        # after crawling is done for one gallery
        #------ save data to db ------#
        #------ to update last post_num ------#
        post_nums[i] = post_num
        # todo : save psotnum for each gallery
        db.rawdata.update_one({"site": name}, {"$set": {"post_num." + str(i): post_nums[i]}})
        db.rawdata.update_one({"site": name}, {"$addToSet": {"board": {"$each": boards}}})

        # save data in local for checking data
        #file_data["board"] += boards

    # after crawling is done for all gallery
    # to save last post_nums
    #file_data["post_num"] = post_nums

    #------ to update last post_num ------#
    #db.rawdata.update_one({"site": name}, {"$addToSet": {"post_nums": post_nums}})

    # save data to json
    #json_string = json.dumps(file_data, ensure_ascii=False, indent="\t")
    json_string = ''

    return json_string
