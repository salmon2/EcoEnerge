from types import MethodType
from pymongo import MongoClient
from bson.objectid import ObjectId

import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import search_charge
import math
import json


app = Flask(__name__)

client = MongoClient('localhost', 27017 )
db = client.EcoEnerge

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/init', methods = ['POST'])
def init():
    city = request.form["city"]
    search_charge.init_data(city)

    return jsonify({'result': 'success', 'msg': "성공"})
    

@app.route('/api/chargeList', methods = ['GET'])
def get_charges():
    page = request.args.get('page', type=int, default=1)  # 페이지
    print("page", page)

    size = 9

    # board컬럭션에 있는 모든 데이터를 가져옴
    datas = db.chargeList.find({}).skip((page - 1) * size).limit(size)
    
    # 게시물의 총 개수 세기
    tot_count = db.chargeList.find({}).count()
    # 마지막 페이지의 수 구하기
    last_page_num = math.ceil(tot_count / size) # 반드시 올림을 해줘야함

    json_object = {
        'size': size,
        'currentPage' : page,
        'maxPage': last_page_num,
    }

    json_string = json.dumps(json_object)

    # return jsonify({'result': 'success'})
    return render_template("dummy_charges.html", info = json_string, data = datas)

@app.route('/api/charge', methods = ['GET'])
def charge():
    print("charge_one")
    
    chargeId = request.args.get("chargeId")
    print(chargeId)
    chargeId = chargeId[10:-2]
    print(chargeId)
    print(type(chargeId))
    # chargeId = chargeId[]
    

    charge = db.chargeList.find_one({'_id': ObjectId(chargeId)})
    reviews = db.review.find({'chargeId': ObjectId(chargeId)})


    print(charge)
    print(reviews[0])

    return render_template("dummy_charge.html", charge = charge, reviews = reviews)

@app.route('/api/review', methods = ['POST'])
def review_save():

    memberId = request.form["memberId"]
    chargeId = request.form["chargeId"]
   
    rate = request.form["rate"]
    contents = request.form["contents"]
    like = request.form["like"]


    doc = {
        "memberId": memberId,
        "chargeId": chargeId,

        "rate" : rate,
        "contents":contents,
        "like" : like
    }

    db.review.insert_one(doc)

    return jsonify({'result': 'success', 'msg': f'리뷰 저장!'})


@app.route('/api/review/update', methods = ['POST'])
def review_update():
    review_id = request.form["_id"]
    review_id = review_id[10:-2]

    rate = request.form["rate"]
    contents = request.form["contents"]
    like = request.form["like"]


    db.review.update({"_id": ObjectId(review_id) }, {"$set":{
                                                            "rate" : rate,
                                                            "contents": contents,
                                                            "like" : like
                                                        }
                                                }
                    )

    return jsonify({'result': 'success', 'msg': f'리뷰 수정 완료!'})

@app.route('/api/review/delete', methods = ['POST'] )
def review_delete():
    review_id = request.form["_id"]
    review_id = review_id[10:-2]

    db.review.delete_one({"_id": ObjectId(review_id)})

    return jsonify({'result': 'success', 'msg': f'리뷰 삭제 완료!'})




    


if __name__ == '__main__':
    app.run('localhost', port=5000, debug=True)