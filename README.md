# crawler_server
crawler_server

- Language : python 3
- IDEA : Py-Charm
- Selenium based : To handle dynamic Web page.


# Sample Crawler source code
Use the following code, to match the interface
- crawler_server/crawler/crawler_modules/data/crawler_ex_inven.py

If you only match the interface, you can easily import your crawler module by adding only that module to the following code.
- crawler_server/crawler/views.py


# Mongo DB
In order to minimize the communication bottleneck, we request update query to DB for each of 20 arrays.

db.rawdata.update_one({"site": name}, {"$set": {"post_num." + str(i): post_num}})

db.rawdata.update_one({"site": name}, {"$addToSet": {"board": {"$each": boards}}})



