from types import MethodType
from pymongo import MongoClient
from bson.objectid import ObjectId
import jwt

import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import math
import json

app = Flask(__name__)

SECRET_KEY = 'SPARTA'

#client = MongoClient('mongodb://test:test@localhost', 27017)

client = MongoClient('localhost', 27017)

db = client.EcoEnerge



# home 화면 이동 (로그아웃 상태일 시 로그인 페이지로 이동)
@app.route('/')
def home():
    #token 확인
    token_receive = request.cookies.get('mytoken')
    try:
        # token data decode
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # login -> index.html
        return render_template('index.html')

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        # logout -> login.html
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

# login page 이동
@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)

# login 처리
@app.route('/sign_in', methods=['POST'])
def sign_in():
    # id, password data 받기
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    #print("username_receive", username_receive)
    #print("password_receive", password_receive)

    #password는 hashcode로 저장되어있음으로, hashcode encode
    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    # id, password 동일 data find
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    # data 존재 시
    if result is not None:
        #token 제작, id 정보와, 유효시간 설정
        payload = {
         'id': username_receive,
         'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        #token jsonify 전송을 위해 'utf-8' 형식으로 변경
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')
        # 결과값 return
        return jsonify({'result': 'success', 'token': token})
    # data 없을 시
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

# 회원가입
@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    
    #password has
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    
    # doc 제작
    doc = {
        "username": username_receive,
        "password": password_hash
    }
    # data 저장
    db.users.insert_one(doc)
    # 결과 문구 return
    return jsonify({'result': 'success'})

# ID 중복확인
@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    #print("check_up")
    #username 받기
    username_receive = request.form['username_give']
    # 존재 유무 확인
    exists = bool(db.users.find_one({"username": username_receive}))
    # 결과 문구 return
    return jsonify({'result': 'success', 'exists': exists})


# 지역 검색 post
@app.route('/search', methods =['POST'])
def search():
    city_receive = request.form['city_give']

    return jsonify({'msg':f'{city_receive} 지역 검색 완료!'})

# 리뷰값 저장
@app.route('/posting', methods =['POST'])
def post() :
    # review data 받기
    review_receive = request.form['review_give']
    # review doc 제작
    doc = {
        'review':review_receive
    }
    # review 저장
    db.review.insert_one(doc)
    # 결과 문구 return
    return jsonify({'msg': '저장 완료!'})


# 충전소 리스트 
@app.route('/chargeList', methods = ['GET'])
def chargeList():
    #page와 key 데이터 받기
    page = request.args.get('page', type=int, default=1)  # 페이지
    key = request.args.get('key')
    # print("page", page)
    # print("key", key)
    size = 6
    try:
        
        # chargeList컬럭션에 있는 모든 데이터를 가져옴
        # LIKE 검색기능
        # pagenation 기능 탑제
        data = db.chargeList.find({"address":{"$regex": key}}).skip((page - 1) * size).limit(size)
        
        # 게시물의 총 개수 세기
        tot_count = db.chargeList.count_documents({"address":{"$regex": key}})
   
    # 예외처리, 조회 실패 유무 처리
    except Exception as e:
        print("An exception occurred ::", e)
        return jsonify({'result' : 'fail', 'msg' : '리뷰 목록 조회 실패'})
    
    # 마지막 페이지의 수 구하기
    last_page_num = math.ceil(tot_count / size)  # 반드시 올림을 해줘야함
    
    # ObjectId to id
    chargeList = []
    for charge in data:
        charge["_id"] = str(charge["_id"])
        chargeList.append(charge)
    #print(charge)

    # chargeList.html 로 rendering
    return render_template("chargeList.html", key = key, currentPage = page, maxPage = last_page_num, chargeList = chargeList)

#charge 문구 작성
@app.route('/charge', methods = ['GET'])
def charge():
    #chargeId 값 받기
    chargeId = request.args.get("id")
    try:
        # data 조회
        charge = db.chargeList.find_one({'_id': ObjectId(chargeId)})
        row_reviewList = db.review.find({'chargeId': ObjectId(chargeId)})
    # 예외처리
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


#리뷰 작성 저장하기
@app.route('/review', methods=['POST'])
def review_save():
    #유저 정보 확인
    token_receive = request.cookies.get('mytoken')

    #충전소id와 저장할 contents
    chargeId = request.form["chargeId"]
    contents = request.form["contents"]


    try:
        #유저정보 조회
        #token decode
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        #user db 조회
        user_info = db.users.find_one({"username": payload["id"]})


        #review doc 제작
        doc = {
            "memberId": user_info["_id"],
            "chargeId": ObjectId(chargeId),

            "writer" : user_info["username"],
            "contents": contents,
        }
        #저장
        db.review.insert_one(doc)

    # 예외처리
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return jsonify({'result' : 'fail', 'msg' : '리뷰 저장 실패'})
    except Exception as e:
        print("An exception occurred ::", e)
        return jsonify({'result' : 'fail', 'msg' : '리뷰 저장 실패'})

    return jsonify({'result' : 'success', 'msg' : '리뷰 저장 성공'})

# 유저 권한 조회
def checkUser(reviewId, token_receive):
    #print("check")
    try:
        #token으로 현제 로그인 된 user 정보 조회
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        
        #review 작성이 정보 조회
        review = db.review.find_one({'_id': ObjectId(reviewId)})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError, Exception ):
        return False

    #print(str(user_info['_id']))
    #print("review info userId ", review)

    #로그인 정보와 작성이 정보 비교
    if  str(user_info['_id']) == str(review['memberId']):
        return True
    else:
        return False

#리뷰 수정하기
@app.route('/review/update', methods = ['POST'])
def review_update():
    #print("update")
    #id 정보 등
    review_id = request.form["_id"]
    chargeId = request.form["chargeId"]
    token_receive = request.cookies.get('mytoken')

    #수정할 data 정보
    rate = request.form["rate"]
    contents = request.form["contents"]

    #권한 체크
    if checkUser(review_id, token_receive):
        #print("check success")
        try:
            #수정 실행
            db.review.update({"_id": ObjectId(review_id)}, {"$set": {
                                                                    "rate": rate,
                                                                    "contents": contents,
                                                                    }
                                                                }
                            )
        #예외처리
        except Exception as e:
            print("An exception occurred ::", e)
            return jsonify({'result' : 'fail', 'msg' : '리뷰 수정 실패'})
    # 각종 결과 message return
        return jsonify({'result' : 'success', 'msg' : '리뷰 수정 완료'})
    else:
        return jsonify({'result' : 'authorization fail', 'msg' : '리뷰 수정 권한 없음'})
    

# 리뷰 삭제하기
@app.route('/review/delete', methods = ['POST'] )
def review_delete():
    #print("delete")
    reviewId = request.form["_id"]
    token_receive = request.cookies.get('mytoken')
    
    #권한 찾기
    if checkUser(reviewId, token_receive):
        #print("check success")
        #리뷰 삭제
        try:
            db.review.delete_one({"_id": ObjectId(reviewId)})
        #예외처리
        except Exception as e:
            return jsonify({'result' : 'fail', 'msg' : '리뷰 삭제 실패'})
        return jsonify({'result': 'success', 'msg': '리뷰 삭제 완료!'})
    else:
        return jsonify({'result': 'uthorization fail', 'msg': '리뷰 삭제 권한 없음'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
