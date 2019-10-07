from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException
import json
from collections import OrderedDict
from datetime import datetime
from time import sleep
import random

def crawler(driver, name, db):
    url = 'https://cafe.naver.com/dieselmania?iframe_url=/ArticleRead.nhn%3Fclubid=11262350%26menuid=91%26boardtype=L%26articleid='

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

        # find latest post_number of post, to set max number
        driver.get('https://cafe.naver.com/dieselmania?iframe_url=/ArticleList.nhn%3Fsearch.clubid=11262350%26search.boardtype=L%26search.menuid=91')
        driver.switch_to.frame(driver.find_element_by_id('cafe_main'))    # switch to inner iframe
        max_post_num = 0
        pn = driver.find_elements_by_class_name('inner_number')
        if len(pn) == 0:
            continue
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
            sleep(random.uniform(1, 3))
            try:
                #------ get each gallery ------#
                driver.get(url + str(post_num))
                # check for alert (nonexistent article)
                try:
                    alert = driver.switch_to.alert
                    alert.accept()
                    continue
                except NoAlertPresentException:
                    # article exist
                    pass
                # check for login popup (unauthorized article)
                if len(driver.window_handles) > 1:
                    main_window = driver.current_window_handle
                    for j in driver.window_handles:
                        if j != main_window:
                            driver.switch_to.window(j)
                            driver.close()
                    driver.switch_to.window(main_window)
                    continue
                driver.switch_to.frame(driver.find_element_by_id('cafe_main'))  # switch to inner frame

                # parsing html part
                title_box = driver.find_element_by_id('tit-box')
                title = title_box.find_element_by_class_name('fl').find_element_by_tag_name('tr').find_elements_by_tag_name('td')[0].get_attribute('innerText')
                date = title_box.find_element_by_class_name('fr').get_attribute('innerText')
                content = driver.find_element_by_class_name('inbox').find_element_by_id('tbody').get_attribute('innerText')

                #------ store data to board[] ------#
                board = OrderedDict()
                board['title'] = title
                board['date'] = datetime.strptime(date, '%Y.%m.%d. %H:%M')
                board['url'] = url + str(post_num)
                board['content'] = content
                boards.append(board)

                #json_string = json.dumps(boards, ensure_ascii=False, indent="\t")
                #print(json_string)

            except NoSuchElementException:
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
