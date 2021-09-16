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
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
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

    print("username_receive", username_receive)
    print("password_receive", password_receive)

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})


    if result is not None:
        payload = {
         'id': username_receive,
         'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
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

# 리뷰값 받는 부분
@app.route('/posting', methods =['POST'])
def post() :
    review_receive = request.form['review_give']

    doc = {
        'review':review_receive
    }

    db.review.insert_one(doc)

    return jsonify({'msg': '저장 완료!'})


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
    try:
        # board컬럭션에 있는 모든 데이터를 가져옴
        data = db.chargeList.find({"address":{"$regex": key}}).skip((page - 1) * size).limit(size)
        # 게시물의 총 개수 세기
        tot_count = db.chargeList.count_documents({"address":{"$regex": key}})
    # 마지막 페이지의 수 구하기
    except Exception as e:
        print("An exception occurred ::", e)
        return jsonify({'result' : 'fail', 'msg' : '리뷰 목록 조회 실패'})
    last_page_num = math.ceil(tot_count / size)  # 반드시 올림을 해줘야함
    
    #Objectid to str
    chargeList = []
    for charge in data:
        charge["_id"] = str(charge["_id"])
        chargeList.append(charge)
        print(charge)
    
    #python document to json
    info = {
        'size': size,
        'currentPage': page,
        'maxPage': last_page_num,
    }
    json_info = json.dumps(info)

    return render_template("chargeList.html", info = json_info, chargeList = chargeList)

@app.route('/charge', methods = ['GET'])
def charge():
    chargeId = request.args.get("id")
    try:
        charge = db.chargeList.find_one({'_id': ObjectId(chargeId)})
        row_reviewList = db.review.find({'chargeId': ObjectId(chargeId)})
    except Exception as e:
        return jsonify({'result' : 'fail', 'msg' : '리뷰 조회 실패'})
    
    # Objectid to String
    #print("charge_id:", charge['_id'])
    charge['_id'] = str(charge['_id'])
    #print("charge_id:", charge['_id'])
    
    # Objectid to pythondocument
    reviewList = []
    for review in row_reviewList:
        review['_id'] = str(review['_id'])
        review['chargeId'] = str(review['chargeId'])
        reviewList.append(review)

    return render_template("charge_detail.html", charge = charge, reviewList = reviewList)


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
        return jsonify({'result' : 'fail', 'msg' : '리뷰 저장 실패'})

    return redirect(url_for("charge", id=chargeId))

@app.route('/review/update', methods = ['POST'])
def review_update():
    review_id = request.form["_id"]
    chargeId = request.form["chargeId"]
    rate = request.form["rate"]
    contents = request.form["contents"]
    like = request.form["like"]

    print("review_id", review_id)

    try:
        db.review.update({"_id": ObjectId(review_id)}, {"$set": {
                                                                "rate": rate,
                                                                "contents": contents,
                                                                "like": like
                                                                }
                                                            }
                        )
    except Exception as e:
        print("An exception occurred ::", e)
        return jsonify({'result' : 'fail', 'msg' : '리뷰 수정 실패'})

    #return jsonify({'result' : 'success', 'msg' : '리뷰 수정 성공'})   
    return redirect(url_for("charge", id = chargeId))

@app.route('/review/delete', methods = ['POST'] )
def review_delete():
    reviewId = request.form["_id"]
    try:
        db.review.delete_one({"_id": ObjectId(reviewId)})
    except Exception as e:
        return jsonify({'result' : 'fail', 'msg' : '리뷰 삭제 실패'})
    return jsonify({'result': 'success', 'msg': '리뷰 삭제 완료!'})


if __name__ == '__main__':
    app.run('localhost', port=5000, debug=True)
