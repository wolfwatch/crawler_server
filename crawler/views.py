from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from django.http import HttpResponse, HttpRequest
import urllib.request
from selenium import webdriver

from .models import Student, RawData
from pymongo import MongoClient

# import crawler modules
# add( write ) .py name about crawler
from crawler.crawler_modules import inven, instiz, pann, ou


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
    client = MongoClient("localhost:27017")
    db = client.crawler_db
    list_cursor = db.rawdata.find({}, {"_id": 0, "site": 1})
    #name_list = list_cursor

    # parallel running by multiprocess or multithread
    for name in list_cursor:
        print(name["site"])
        # crawler(name["site"], db)

    return HttpResponse('done')


def crawler(name, db):
    # open chrom
    doptions = webdriver.ChromeOptions()
    doptions.add_extension('ublock.crx')
    doptions.add_extension('blockimage.crx')
    driver = webdriver.Chrome('C://driver/chromedriver', options=doptions)

    # Each 'site' has a crawler 'module'
    if name == 'inven':
        end_crawling(inven.crawler(driver, name, db), name)
    elif name == 'instiz':
        end_crawling(instiz.crawler(driver, name, db), name)
    elif name == 'pann':
        end_crawling(pann.crawler(driver, name, db), name)
    elif name == 'ou':
        end_crawling(ou.crawler(driver, name, db), name)
    elif name == 'dotax':
        end_crawling(ou.crawler(driver, name, db), name)
    elif name == 'ilbe':
        end_crawling(ou.crawler(driver, name, db), name)
    # keep adding more crawler module

    driver.close()

@csrf_exempt
def result(request):
    data = request.POST
    print(data)
    return HttpResponse("reqeusted! anyway!!")


def end_crawling(json_string, name):

    # save data in local disk
    f = open('data/'+name+'.json', 'w', encoding="utf-8")
    f.write(json_string)

    # save data in DB
    # HttpResponse(json.dumps(result), content_type='application/json')

    return f.close()


