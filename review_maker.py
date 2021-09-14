from pymongo import MongoClient
import requests
from random import *

client = MongoClient('localhost', 27017)
db = client.EcoEnerge

datas = db.chargeList.find({})
print(datas[0])
total_count = db.chargeList.find({}).count()

k = 1
for i in range(total_count):
    for j in range(3):
        memberId = randint(1,4)
        chargeId = datas[i]['_id']
        
        rate = randint(1,6)
        contents =  "contents " + str(k)
        like = 0

        doc = {
            'chargeId' : chargeId,
            'memberId' : memberId,

            'contents' : contents,
            'rate' : rate,
            'like' : like
        }
        db.review.insert_one(doc)
        k = k + 1
