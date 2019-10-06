from threading import Thread
from urllib.parse import quote_plus

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from django.http import HttpResponse, HttpRequest
import urllib.request
from selenium import webdriver

from .models import Student, RawData
from pymongo import MongoClient

# import crawler modules
# add( write ) .py name about crawler
from crawler.crawler_modules import inven, instiz, pann, ou, dotax, ilbe


# Create your views here.
def home(request):
    student_data = Student.objects.all()
    for field in student_data:
        print('name of student is: ', field.name)
    return HttpResponse("this url is working")


@csrf_exempt
def index(request):
    # show Req
    print(request)

    # connect MongoDB
    uri = "mongodb://%s:%s@%s" % (quote_plus("admin123"), quote_plus("1234"), "wolfwatch.dlinkddns.com:27017/admin")
    client = MongoClient(uri)
    db = client.crawler_db
    list_cursor = db.rawdata.find({}, {"_id": 0, "site": 1})
    #name_list = list_cursor

    # parallel running by multiprocess or multithread
    threads = []
    for name in list_cursor:
        print(name["site"])
        crawler(name["site"], db)
        th_one = Thread(target=crawler, args=(name["site"], db))
        th_one.start()
        threads.append(th_one)
        # crawler(name, db) <- views.py에 해당하는 부분
        # Thread t가 종료될 때까지 기다리기
    for t in threads:
        t.join()

    return HttpResponse('done')


def crawler(name, db):
    # open chrom
    doptions = webdriver.ChromeOptions()
    doptions.add_extension('ublock.crx')
    doptions.add_extension('blockimage.crx')

    # check DB and Name
    if check_newSite(db, name) :
        # Each 'site' has a crawler 'module'
        if name == 'inven':
            driver = webdriver.Chrome('C://driver/chromedriver', options=doptions)
            end_crawling(inven.crawler(driver, name, db), name)
        elif name == 'instiz':
            driver = webdriver.Chrome('C://driver/chromedriver', options=doptions)
            end_crawling(instiz.crawler(driver, name, db), name)
        elif name == 'pann':
            driver = webdriver.Chrome('C://driver/chromedriver', options=doptions)
            end_crawling(pann.crawler(driver, name, db), name)
        elif name == 'ou':
            driver = webdriver.Chrome('C://driver/chromedriver', options=doptions)
            end_crawling(ou.crawler(driver, name, db), name)
        elif name == 'dotax':
            driver = webdriver.Chrome('C://driver/chromedriver', options=doptions)
            end_crawling(dotax.crawler(driver, name, db), name)
        elif name == 'ilbe':
            driver = webdriver.Chrome('C://driver/chromedriver', options=doptions)
            end_crawling(ilbe.crawler(driver, name, db), name)
        # keep adding more crawler module

    driver.close()


@csrf_exempt
def result(request):
    data = request.POST
    print(data)
    return HttpResponse("reqeusted! anyway!!")


def end_crawling(json_string, name):

    # save data in local disk
    #f = open('data/'+name+'.json', 'w', encoding="utf-8")
    # f.write(json_string)

    print(name + " : " + str(json_string))
    # save data in DB
    # HttpResponse(json.dumps(result), content_type='application/json')

    # return f.close()
    return 


# just check
def check_newSite(db, name):

    # 1. Insert empty json model -> first crawling, run this independently
    # ------ check site name && rawdata ------ #
    cursor = db.rawdata.find({"site": name})
    empty_name = cursor[0]["site"]
    if empty_name == name:
        print("already exist")
        return True
    else:
        print("it's new one, before crawl site store empty data to db")
        return False

