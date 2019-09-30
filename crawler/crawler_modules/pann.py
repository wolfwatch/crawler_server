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
    post_nums = cursor["post_nums"]

    # wait finding element, for max 5sec
    driver.implicitly_wait(3)

    # find latest post_number of post, to set max number
    driver.get(url + gallery_url[0] + 'c20001')
    latest_post = driver.find_element_by_xpath('//tr[@class="first"]/td[1]/a[1]').get_attribute('href')

    max_post_num1 = latest_post.replace('https://pann.nate.com/talk/', '')
    max_post_num = max_post_num1.replace('?page=1', '')
    print(max_post_num)
    post_nums[0] = max_post_num - 10

    # check latest
    if post_nums[0] < int(max_post_num) - 1:

        j = post_nums[0]
        for j in range(post_nums[0], int(max_post_num)):
            board = OrderedDict()
            try:
                # get each gallery
                driver.get(url + gallery_url[0] + str(j))
                title = driver.find_element_by_xpath('//div[@class="view-wrap"]/div[1]/h4[1]').get_attribute('title')
                date = driver.find_element_by_xpath('//span[@class="date"]').text
                content = driver.find_element_by_xpath('//div[@id="contentArea"]').text

                board['title'] = title
                board['date'] = date
                board['url'] = url + gallery_url[0] + str(j)
                board['content'] = content
                boards.append(board)
                print(content)
            except UnexpectedAlertPresentException:
                print("no post")
            except NoSuchElementException:
                try:
                    content = driver.find_element_by_xpath('//*[@id="contentArea"]/p[1]').text
                    board['content'] = content
                    boards.append(board)
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

            json_string = json.dumps(board, ensure_ascii=False, indent="\t")
            print(json_string)

        # to save last post_num
        post_nums[0] = j
        db.rawdata.update_one({"site": name}, {"$addToSet": {"board": {"$each": boards}}})

    # to save last post_nums
    db.rawdata.update_one({"site": name}, {"$addToSet": {"post_nums": post_nums}})

    # close chrom
    driver.close()


