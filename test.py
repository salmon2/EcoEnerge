from pymongo import MongoClient
from flask import Flask, render_template, jsonify, request, redirect, url_for

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.Test


@app.route('/', methods=['POST'])
def home():
    # data 입력받기
    chargeName = request.form['chargeName']
    address = request.form['address']

    # data, doc form으로 변경
    doc = {
        "username": chargeName,
        "password": address
    }

    #insert
    db.chargeList.insert_one(doc)
    
    return jsonify({'result': 'success'})


if __name__ == '__main__':
    app.run('localhost', port=5000, debug=True)