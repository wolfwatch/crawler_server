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
    post_nums = cursor["post_nums"]

    # wait finding element, for max 5sec
    driver.implicitly_wait(2)

    # for : 첫번째 겔러리 ~ n번째 갤러리
    for i in range(0, len(gallery_url)):

        # find latest post_number of post, to set max number
        driver.get(url + gallery_url[i])
        max_post_num = driver.find_element_by_xpath('//tr[@class="ls tr tr2"][1]/td[1]').text
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

                title = driver.find_element_by_xpath('//*[@class="articleTitle"]/h1[1]').text
                date = driver.find_element_by_xpath('//*[@class="articleDate"]').text
                content = driver.find_element_by_xpath('//*[@id="powerbbsContent"]').text

                board = OrderedDict()
                board['title'] = title
                board['date'] = date
                board['url'] = url + gallery_url[i] + str(j)
                board['content'] = content
                boards.append(board)

                json_string = json.dumps(boards, ensure_ascii=False, indent="\t")
                print(json_string)

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
        # to save last post_num
        post_nums[i] = j
        # to add new posts
        db.rawdata.update_one({"site": name}, {"$addToSet": {"board": {"$each": boards}}})

    # to save last post_nums
    db.rawdata.update_one({"site": name}, {"$addToSet": {"post_nums": post_nums}})

    # close chrom
    driver.close()
    # save data to json
    json_string = json.dumps(file_data, ensure_ascii=False, indent="\t")

    return json_string
