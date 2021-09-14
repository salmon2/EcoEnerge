from types import MethodType
from pymongo import MongoClient
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import search_charge


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



    


if __name__ == '__main__':
    app.run('localhost', port=5000, debug=True)