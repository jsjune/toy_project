from math import *
from flask import *
import hashlib
import jwt
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import item_list

app = Flask(__name__)
client = MongoClient('mongodb+srv://test:sparta@cluster0.tfnms.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.toy_project

headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
data = requests.get('https://www.shoeprize.com/drops/', headers=headers)
soup = BeautifulSoup(data.text, 'html.parser')

items = soup.select('ul.calendar_list > li')

item_list.crawling()

SECRET_KEY = 'SPARTA'

@app.route('/')
def home():
    if request.cookies.get('token') is None:
        return render_template('index.html')
    else:
        token = request.cookies.get('token')
        member = jwt.decode(token, SECRET_KEY, algorithms = 'HS256')
        id = member['ID']
        if db.member.find_one({'ID': id}).get('draw_items'):
            draw_items = list(db.member.find_one({'ID': id}).get('draw_items'))
            return render_template('index.html', member=member, draw_items=draw_items)
        else:
            return render_template('index.html', member=member)

@app.route("/list", methods=["GET"])
def item_list():
    page = request.args.get("page", 1, type=int)
    item_list = list(db.items.find({}, {'_id': False}).skip((page-1)*12).limit(12))
    items_count = len(list(db.items.find({}, {'_id': False})))
    last_page = ceil(items_count/12)
    return jsonify({'items': item_list, 'last_page': last_page})

@app.route("/delete_draw", methods=["POST"])
def delete_draw():
    id = request.form['id']
    item = request.form['product_name']
    db.member.update_one({'ID': id}, {'$pull': {'draw_items': item}})
    return jsonify({'msg': '삭제가 완료되었습니다.'})

@app.route('/draw', methods=["POST"])
def draw():
    product_name = request.form['product_name']
    id = request.form['id']
    item = db.items.find_one({'product_name': product_name})

    if item.get('draw_member') is None:
        db.items.update_one({'product_name': product_name}, {'$push': {'draw_member': id}})
        db.member.update_one({'ID': id}, {'$push': {'draw_items': product_name}})
        return jsonify({'msg': '응모가 완료되었습니다!'})

    else:
        if id in item['draw_member']:
            return jsonify({'msg': '이미 응모 되어있는 상품입니다.'})

        db.items.update_one({'product_name': product_name}, {'$push': {'draw_member': id}})
        db.member.update_one({'ID': id}, {'$push': {'draw_items': product_name}})
        return jsonify({'msg': '응모가 완료되었습니다!'})


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
    pw_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    name = request.form['name']
    doc={
        'ID':id,
        'password':pw_hash,
        'name':name
    }
    db.member.insert_one(doc)
    return render_template('login_resist_form.html')

@app.route("/sign_in", methods=["POST", "GET"])
def login():
    if request.method == 'POST':
        id = request.form['id']
        pw = request.form['pw']

        pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()

        result = db.member.find_one({'ID': id, 'password': pw_hash})

        if result is not None:
            payload = {
                'ID': result['ID'],
                'name': result['name'],
                'exp': datetime.utcnow() + timedelta(hours=24) # 로그인 24시간 유지
            }

            token = jwt.encode(payload, SECRET_KEY, algorithm = 'HS256')

            resp = make_response(redirect(url_for('home')) )
            resp.set_cookie('token', token)
            return resp
        else:
            return render_template('login_resist_form.html', msg='아이디 또는 비밀번호가 일치하지 않습니다.')
    else:
        return render_template('login_resist_form.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
