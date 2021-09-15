from types import MethodType
from pymongo import MongoClient
from bson.objectid import ObjectId
import jwt

import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import chargeList_maker
import math
import json

app = Flask(__name__)

SECRET_KEY = 'SPARTA'


client = MongoClient('localhost', 27017)
db = client.EcoEnerge
# 토큰 가져오기
@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        return render_template('index.html')
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.execeptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

# 로그인
@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/sign_in', methods=['POST'])
def sign_in():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
            'id': username_receive, 
            # 로그인 24시간 유지
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm= 'HS256').decode('utf-8')

        return jsonify({'result': 'success', 'token': token})
    # 토큰을 찾지 못한다면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

# 회원가입
@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,
        "password": password_hash
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})

# ID 중복확인
@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    
    return jsonify({'result': 'success', 'exists': exists})


@app.route('/search', methods =['POST'])
def search():
    city_receive = request.form['city_give']

    return jsonify({'msg':f'{city_receive} 지역 검색 완료!'})


@app.route('/init', methods=['POST'])
def init():
    city = request.form["city"]
    chargeList_maker.init_data(city)

    return jsonify({'result': 'success', 'msg': "성공"})

@app.route('/chargeList', methods = ['GET'])
def chargeList():
    page = request.args.get('page', type=int, default=1)  # 페이지
    key = request.args.get('key')
    print("page", page)
    print("key", key)
    size = 9

    # board컬럭션에 있는 모든 데이터를 가져옴
    data = db.chargeList.find({"address":{"$regex": key}}).skip((page - 1) * size).limit(size)
    chargeList = []
    for charge in data:
        charge["_id"] = str(charge["_id"])
        chargeList.append(charge)
        print(charge)
    # 게시물의 총 개수 세기
    tot_count = db.chargeList.count_documents({"address":{"$regex": key}})
    # 마지막 페이지의 수 구하기
    last_page_num = math.ceil(tot_count / size)  # 반드시 올림을 해줘야함

    info = {
        'size': size,
        'currentPage': page,
        'maxPage': last_page_num,
    }
    json_info = json.dumps(info)


    return render_template("dummy_charges.html", info = json_info, chargeList = chargeList)

@app.route('/charge', methods = ['GET'])
def charge():
    print("charge_one")
    
    chargeId = request.args.get("id")

    charge = db.chargeList.find_one({'_id': ObjectId(chargeId)})
    charge['_id'] = str(charge['_id'])
    
    
    reviewList = []
    row_reviewList = db.review.find({'chargeId': ObjectId(chargeId)})
    for review in row_reviewList:
        review['_id'] = str(review['_id'])
        review['chargeId'] = str(review['chargeId'])
        reviewList.append(review)


    return render_template("dummy_charge.html", charge = charge, reviewList = reviewList)


@app.route('/review', methods=['POST'])
def review_save():
    token_receive = request.cookies.get('mytoken')
    chargeId = request.form["chargeId"]
    rate = request.form["rate"]
    contents = request.form["contents"]
    like = request.form["like"]

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})

        doc = {
            "memberId": user_info["_id"],
            "chargeId": ObjectId(chargeId),

            "rate": rate,
            "contents": contents,
            "like": like
        }

        db.review.insert_one(doc)

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("charge", id = chargeId))

    return redirect(url_for("login"))

@app.route('/review/update', methods = ['POST'])
def review_update():
    review_id = request.form["_id"]
    charge_id = request.form["chargeId"]
    rate = request.form["rate"]
    contents = request.form["contents"]
    like = request.form["like"]

    db.review.update({"_id": ObjectId(review_id)}, {"$set": {
                                                            "rate": rate,
                                                            "contents": contents,
                                                            "like": like
                                                            }
                                                        }
                    )

    return redirect(url_for("charge", id = "charge_id"))

@app.route('/review/delete', methods = ['POST'] )
def review_delete():
    review_id = request.form["_id"]

    db.review.delete_one({"_id": ObjectId(review_id)})

    return jsonify({'result': 'success', 'msg': '리뷰 삭제 완료!'})




if __name__ == '__main__':
    app.run('localhost', port=5000, debug=True)