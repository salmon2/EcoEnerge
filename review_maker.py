from types import MemberDescriptorType
from pymongo import MongoClient
import requests
from random import *

client = MongoClient('localhost', 27017)
db = client.EcoEnerge

chargeList = db.chargeList.find({})
total_count = db.chargeList.find({}).count()

k = 1
for i in range(total_count):
    for j in range(3):
        memberId = randint(1,4)
        chargeId = chargeList[i]['_id']

       
        contents =  "contents " + str(k)
        writer = "Member " + str(k)

        doc = {
            'chargeId' : chargeId,
            'memberId' : memberId,

            "writer" : writer,
            'contents' : contents,
        }
        db.review.insert_one(doc)
        k = k + 1
