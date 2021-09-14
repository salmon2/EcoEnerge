from types import MethodType
from pymongo import MongoClient
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import search_charge
import math


app = Flask(__name__)


client = MongoClient('localhost', 27017)
db = client.EcoEnerge


@app.route('/')
def home():
    return render_template("index.html")

@app.route('/init', methods = ['POST'])
def init():
    city = request.form["city"]
    search_charge.init_data(city)

    return jsonify({'result': 'success', 'msg': "성공"})
    

@app.route('/api/charges', methods = ['GET'])
def get_charges():
    page = request.args.get('page', type=int, default=1)  # 페이지
    print("page", page)

    size = 10

    # board컬럭션에 있는 모든 데이터를 가져옴
    datas = db.chargeList.find({}).skip((page - 1) * size).limit(size)  

    # 게시물의 총 개수 세기
    tot_count = db.chargeList.find({}).count()
    # 마지막 페이지의 수 구하기
    last_page_num = math.ceil(tot_count / size) # 반드시 올림을 해줘야함

     # 페이지 블럭을 5개씩 표기
    block_size = 5
    # 현재 블럭의 위치 (첫 번째 블럭이라면, block_num = 0)
    block_num = int((page - 1) / block_size)
    # 현재 블럭의 맨 처음 페이지 넘버 (첫 번째 블럭이라면, block_start = 1, 두 번째 블럭이라면, block_start = 6)
    block_start = (block_size * block_num) + 1
    # 현재 블럭의 맨 끝 페이지 넘버 (첫 번째 블럭이라면, block_end = 5)
    block_end = block_start + (block_size - 1)

    print("block_size", block_size)
    print("block_num", block_num)
    print("block_start", block_start)
    print("block_end", block_end)
    print("datas", datas[0])

    
    
    return jsonify({'result': 'success'})

#    return render_template("index.html", words = charges)



    


if __name__ == '__main__':
    app.run('localhost', port=5000, debug=True)