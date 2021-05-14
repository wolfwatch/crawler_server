import datetime

from selenium.common.exceptions import NoSuchElementException
import json
from collections import OrderedDict

from time import sleep

from selenium.webdriver.common.keys import Keys


def crawler(driver, name, db):
    # todo : change url
    url = 'http://cafe.daum.net/dotax/'


    ## 로그인 파트
    driver.get('https://logins.daum.net/accounts/signinform.do?url=https%3A%2F%2Fwww.daum.net%2F')
    driver.find_element_by_name('id').send_keys('--------')
    driver.find_element_by_name('pw').send_keys('-------')
    dd = driver.find_element_by_name('pw')
    dd.send_keys(Keys.RETURN)
    sleep(1)

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
        driver.switch_to.frame(driver.find_element_by_id('down'))
        max_post_num = 0
        pn = driver.find_element_by_class_name('bbsList').find_elements_by_class_name('num')
        for k in pn:
            if k.text.isdigit() and int(k.text) > max_post_num:
                max_post_num = int(k.text)
        print("max number :  " + str(max_post_num))

        #post_nums[i] = max_post_num - 10

        #------ check latest ------#
        if post_nums[i] >= int(max_post_num) - 1:
            continue

        post_num = post_nums[i]
        for post_num in range(post_nums[i], int(max_post_num)):
            try:
                #------ get each gallery ------#
                driver.get(url + gallery_url[i] +'/'+ str(post_num))
                driver.switch_to.frame(driver.find_element_by_id('down'))
                # parsing html part
                title = driver.find_element_by_xpath('//*[@class="subject"]/span[2]').text
                u = driver.find_element_by_xpath('//*[@class="article_writer"]/span[6]').text
                date = datetime.datetime.strptime(u, "%Y.%m.%d. %H:%M")
                content = driver.find_element_by_class_name('protectTable').get_attribute('innerText')

                #------ store data to board[] ------#
                board = OrderedDict()
                board['title'] = title
                board['date'] = date
                board['url'] = url + gallery_url[i] +'/'+ str(post_num)
                board['content'] = content
                boards.append(board)

                json_string = json.dumps(boards, ensure_ascii=False, indent="\t")
                print(json_string)

            except NoSuchElementException:
                continue

                        # ------ save it every 20 count ------#
            if len(boards) > 20: #중간에 꺼질 경우 대비해 json에 저장 및 postnum update
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

    # save data to json
    json_string = json.dumps(file_data, ensure_ascii=False, indent="\t")

    return json_string
