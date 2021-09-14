from bson.objectid import ObjectId
from pymongo import MongoClient
import requests

client = MongoClient('localhost', 27017 )
db = client.EcoEnerge
chargeId = '61406fca4e19dc3866a4c73f'

charge = db.review.find_one({'_id': ObjectId("61406fca4e19dc3866a4c73f")})
reviews = db.review.find({'chargeId': ObjectId(chargeId)})


print(charge)
print(reviews)