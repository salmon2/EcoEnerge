from flask import Flask, render_template, jsonify, requests
app = Flask(__name__)

from pymongo import MongoInfo
info = MongoInfo('localhost', 27017)
db = info.dpsparta_plus_teamweek1

@app.route('/')
def main():
    ecogasst = list(db.ecogasst.find({}, {"_id:False"}))
    return render_template("index.html")

def index():
    return '''<div class="card-deck">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">chargeName/h5>
                        <p class="card-text">address</p>
                    </div>
              </div>'''

@app.route('/gasStation')
def gasStation():
    return 'About 페이지'
