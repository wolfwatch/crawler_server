import traceback
import json

from pymongo import MongoClient
from urllib.parse import quote_plus
from selenium import webdriver

#단어를 입력 받는다
word_searched = input('크롤링 할 단어를 입력하세요 : ')

#디비 정보를 받아온다.
try:
    # client = MongoClient("localhost:27017")
    # client = MongoClient("admin123:1234@wolfwatch.dlinkddns.com:27017/admin")
    uri = "mongodb://%s:%s@%s" % (quote_plus("admin123"), quote_plus("1234"), "wolfwatch.dlinkddns.com:27017/admin")
    client = MongoClient(uri)
    # 디비 연결
    db = client.crawler_db
except:
    traceback.print_exc()




#a = db.word_last_date_table.find({"word": "조국"}).countDocuments()
#print(a)
#디비의 word_last_date_table에서 해당 단어의 data가 있는지 찾는다.
#직접적으로 찾는 정보가 있을 때 true를 반환하는 함수는 없다.
if(db.word_last_date_table.count_documents({"word": word_searched}) > 0) :
    list_cursor = db.word_last_date_table.find_one({'word': word_searched})
    print("예전에 찾았던 단어입니다.")
    l_d = list_cursor["last_date"]
    str_ld = list_cursor["last_date"].strftime("%M - %D - %Y")
    print("최근에 찾았던 날자는 ", str_ld )

else :
    print("처음 검색하는 단어입니다.")


