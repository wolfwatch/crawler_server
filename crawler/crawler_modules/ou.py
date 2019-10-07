import datetime

from selenium.common.exceptions import NoSuchElementException
import json
from collections import OrderedDict


def crawler(driver, name, db):

    u = 'http://www.todayhumor.co.kr/board/'
    r1 = 'list'
    r2 = 'view'
    l= '.php?table='



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
        url = u + r1 + l
        print(url + gallery_url[i])
        # find latest post_number of post, to set max number
        driver.get(url + gallery_url[i])
        max_post_num = driver.find_element_by_xpath('//td[@class="no"]/a[1]').text
        print("max number :  " + max_post_num)

        #post_nums[i] = max_post_num - 10

        #------ check latest ------#
        if post_nums[i] >= int(max_post_num) - 1:
            continue
        url = u+ r2 + l
        post_num = post_nums[i]
        for post_num in range(post_nums[i], int(max_post_num)):
            try:
                #------ get each gallery ------#
                driver.get(url + gallery_url[i] +'&no='+ str(post_num))

                # parsing html part
                title = driver.find_element_by_xpath('//*[@class="viewSubjectDiv"]/div').text
                date = driver.find_element_by_xpath('//*[@class="writerInfoContents"]/div[7]').text
                content = driver.find_element_by_xpath('//*[@class="viewContent"]').text

                #------ store data to board[] ------#
                board = OrderedDict()
                board['title'] = title
                board['date'] = datetime.datetime.strptime(date[7:], "%Y/%m/%d %H:%M:%S")
                board['url'] = url + gallery_url[i] +'&no='+ str(post_num)
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
