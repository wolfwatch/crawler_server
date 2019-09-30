from selenium.common.exceptions import NoSuchElementException
import json
from collections import OrderedDict
from pymongo import MongoClient

def crawler(driver, name, db):
    # main address of inven
    url = 'https://www.instiz.net/'

    # list of galleries of inven
    # gallery_url = ['pt/', 'name/', 'name_enter/', 'name_beauty/']
    #   => cursor["gallery_url"]
    # default_post_nums = [6415980, 33265157, 66012035, 1249425]
    #   => cursor["post_num"]

    # add gallery -> it's moved to mongoDB, when you add mor gallery, update mongoDB


    # declare
    boards = []
    file_data = OrderedDict()

    try:
        cursor = db.rawdata.find_one({"site": name}, {"_id": 0, "post_num": 1, "gallery_url": 1})
        gallery_url = cursor["gallery_url"]
        post_nums = cursor["post_nums"]

    except FileNotFoundError:
        json_str = ''
        file_data["site"] = name
        file_data["board"] = []

    # wait finding element, for max 5sec
    driver.implicitly_wait(3)

    # for : 첫번째 겔러리 ~ n번째 갤러리
    for i in range(0, len(gallery_url)):

        # find latest post_number of post, to set max number
        driver.get(url + gallery_url[i])

        max_post = driver.find_element_by_xpath('//td[@class="listno regdate"]')
        max_post_num = max_post.get_attribute('no')
        print(int(max_post_num))
        post_nums[i] = max_post_num - 10

        # check latest
        if post_nums[i] >= int(max_post_num) - 1:
            continue

        j = post_nums[i]
        for j in range(post_nums[i], int(max_post_num)):
            try:
                # get each gallery
                driver.get(url + gallery_url[i] + str(j))
                title = driver.find_element_by_xpath('//*[@id="nowsubject"]/a[1]').text
                date_1 = driver.find_element_by_xpath('//*[@class="tb_left"]/span[1]').get_attribute('title')
                date_2 = driver.find_element_by_xpath('//*[@class="tb_left"]/span[3]').get_attribute('title')

                if len(date_1) > len(date_2):
                    date = date_1
                else:
                    date = date_2

                content = driver.find_element_by_xpath('//p[@*]').text

            except NoSuchElementException:
                try:
                    content = driver.find_element_by_xpath('//*[@class="memo_content"]').text
                    print(content)
                except NoSuchElementException:
                    try:
                        # check is_board
                        driver.find_element_by_xpath('//*[@class="topalert"]')
                        print("no post")
                    except NoSuchElementException:
                        try:
                            # check is_board
                            driver.find_element_by_xpath('//*[@class="memo_content"]')
                        except NoSuchElementException:
                            print("no response")
                            break
            board = OrderedDict()
            board['title'] = title
            board['date'] = date
            board['url'] = url + gallery_url[i] + str(j)
            board['content'] = content
            boards.append(board)

        # to save last post_num
        post_nums[i] = j
        # to add posts of other gallery
        db.rawdata.update_one({"site": name}, {"$addToSet": {"board": {"$each": boards}}})

    # to save last post_nums
    db.rawdata.update_one({"site": name}, {"$addToSet": {"post_nums": post_nums}})

    # close chrom
    driver.close()

    return
