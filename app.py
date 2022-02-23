from math import *

from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient
client = MongoClient('mongodb+srv://test:sparta@cluster0.tfnms.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.toy_project

headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
data = requests.get('https://www.shoeprize.com/drops/', headers=headers)
soup = BeautifulSoup(data.text, 'html.parser')

items = soup.select('ul.calendar_list > li')

for item in items:
    image = item.select_one('div.img_area > img')['data-src'].strip()
    brand = item.select_one('div.info_area > div.product_info > div.brand').text.strip()
    product_name = item.select_one('div.info_area > div.product_info > div.name').text.strip()
    draw_month = item.select_one('div.info_area > div.date_info > span.month').text.strip()
    draw_date = item.select_one('div.info_area > div.date_info > span.date').text.strip()
    doc = {
        'image': image,
        'brand': brand,
        'product_name': product_name,
        'draw_month': draw_month,
        'draw_date': draw_date
    }

    if db.items.find_one({'product_name': product_name}) is None:
        db.items.insert_one(doc)



@app.route('/')
def home():
    return render_template('index.html')


@app.route("/list", methods=["GET"])
def item_list():
    page = request.args.get("page", 1, type=int)
    item_list = list(db.items.find({}, {'_id': False}).skip((page-1)*12).limit(12))
    items_count = len(list(db.items.find({}, {'_id': False})))
    last_page = ceil(items_count/12)
    return jsonify({'items': item_list, 'last_page': last_page})

@app.route('/draw', methods=["GET"])
def draw():
    product_name = request.form['product_name']
    db.users.update_one({'product_name':product_name},{'$push':{'draw_member':id}})
    return render_template('index.html')

@app.route('/signup_form')
def signup_form():
    return render_template('login_resist_form.html')

@app.route('/dupli_check', methods=["POST"])
def duplication_check():
    id = request.form['id']
    if db.member.find_one({'ID':id}) is None:
        return jsonify({'msg' : "사용 가능한 아이디입니다.", 'result' : 1})
    else:
        return jsonify({'msg' : "중복된 아이디가 존재합니다.", 'result' : 0})

@app.route('/sign_up', methods=["POST"])
def sign_up():
    id = request.form['id']
    password = request.form['pw']
    name = request.form['name']
    doc={
        'ID':id,
        'password':password,
        'name':name
    }
    db.member.insert_one(doc)
    return render_template('login_resist_form.html')



if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
