import traceback
import json

from pymongo import MongoClient
from urllib.parse import quote_plus
from selenium import webdriver
from crawler.crawler_modules import inven


def end_crawling(json_string, name):

    f = open('data/'+name+'.json', 'w', encoding="utf-8")
    f.write(json_string)

    return f.close()


def insert_newSite(db, name):

    # 1. Insert empty json model -> first crawling, run this independently
    f = open('data/empty.json', 'r', encoding="utf-8")
    json_str = f.read()
    # print(json_str)
    file_data = json.loads(json_str, encoding="utf-8")
    empty_name = file_data["site"]
    f.close()

    # ------ check site name && rawdata ------ #
    try:
        if empty_name == name:
            cursor = db.rawdata.find({"site": empty_name})
            empty_name = cursor[0]["site"]
            print("already exist")
            return
        else:
            print("check \"sitename\" in empty.json and \"name\" in format.py")
            exit(-1)
    except IndexError:
        print("it's new one, store empty data to db")
        db.rawdata.insert_one(file_data)

def test_mongo():

    # 몽고DB연동
    try:
        # client = MongoClient("localhost:27017")
        # client = MongoClient("admin123:1234@wolfwatch.dlinkddns.com:27017/admin")
        uri = "mongodb://%s:%s@%s" % (quote_plus("admin123"), quote_plus("1234"), "wolfwatch.dlinkddns.com:27017/admin")
        client = MongoClient(uri)
        # 디비 연결
        db = client.crawler_db

        # todo : change sitename
        name = "sitename"

        # 1. Insert empty json model -> first crawling, run this independently
        insert_newSite(db, name)

        ###########################################################################
        # 2. Get "site" name list
        # db.<콜렉션 이름>.find({},{"<표시할 field>":1, "<표시하지 않을 field>":0})
        # {}는 첫번째 인자인 검색 쿼리
        # "_id"는 입력하지 않을 경우, default로 나옴.
        # 나머지는 입력하지 않을 경우, default로 나오지 않음.

        list_cursor = db.rawdata.find({}, {"_id": 0, "site": 1})

        # str_site_list = json.loads(list_cursor)
        # => 실행시 error 발생 : find() 모듈은 객체가 아니라, cursor를 반환한다.
        # print(str_site_list)
        # 즉, 크기가 큰 doc이나 collection에 find로 접근 해도 바로 메모리에 load 하지 않는다.

        # cursor를 list 객체 처럼 쓰려면
        # var myCursor = db.inventory.find( { type: 2 } );
        # var documentArray = myCursor.toArray();
        # myCursor.toArray()[1];

        # print cursor's object to json
        # dumps(cursor)  // from bson.json_util import dumps

        # check site lite
        print(list_cursor[0]["site"])  # list_cursor[0] -> dict 객체를 가져옴
        name = list_cursor[0]["site"]
        for site_name in list_cursor:  # cursor 를 이용해서 해당 객체에 하나씩 접근
            print("site: "+site_name["site"])

        ###########################################################################
        # 3. Get post_num[], using "site" : name
        cursor = db.rawdata.find_one({"site": name}, {"_id": 0, "post_num": 1, "gallery_url": 1})
        # cursor is dict : cursor[]
        print(cursor["post_num"][0])
        print(cursor["gallery_url"][0])

        ###########################################################################
        # 4. crawling
        # def crawler(name, db) <- 이 모듈 안에 넣는 부분

        # open chrom
        # open chrom
        doptions = webdriver.ChromeOptions()
        doptions.add_extension('ublock.crx')
        doptions.add_extension('blockimage.crx')
        driver = webdriver.Chrome('C://driver/chromedriver', options=doptions)

        # elif name == 'sitename'
        end_crawling(inven.crawler(driver, name, db), name)



        ###########################################################################
        # 4. append Boards[], to "board" of collection

        # this funcion is declared in crawler mudule
        # boards = file_data["board"]

        # add each object of Dict board[] to "board" where "site"== name,
        # db.rawdata.update_one({"site": name}, {"$addToSet": {"board": {"$each": boards}}})
        # db.rawdata.update_many({"site": name}, {"$push": {"board": boards}})

        driver.close()

    except:
        traceback.print_exc()


test_mongo()













