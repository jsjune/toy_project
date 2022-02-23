from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
from pymongo import MongoClient

# 비밀번호 암호화에 사용하는 hash 함수 import
import hashlib
import jwt
import datetime

import certifi
ca = certifi.where()
client = MongoClient('mongodb+srv://test:sparta@cluster0.tfnms.mongodb.net/Cluster0?retryWrites=true&w=majority',
                     tlsCAFile=ca)
db = client.toy_project

# 날짜와 시간 다루는 함수 import
from datetime import datetime, timedelta

SECRET_KEY = 'SPARTA'

@app.route('/')
def home():
    return render_template('index.html')


@app.route("/log_in", methods=["POST"])
def login():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    # password는 hash 함수로 암호화
    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()

    # 매칭되는 id와 pw 값이 있는 지 확인
    # 매칭 성공 시 로그인 성공
    result = db.toy_project.find_one({'username': username_receive, 'password': pw_hash})

    # 만약 result가 none이 아니라면(존재한다면)
    if result is not None:
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24) # 로그인 24시간 유지
        }

        # decode 방법이 jwt.decode(token, secret key, algorithms 으로 바뀜)
        # 로그인이 성공했다면 id와 jwt token 만들어서 발행해줌
        # SECRET_KEY로 암호화

        token = jwt.encode(payload, SECRET_KEY, algorithm ='HS256')

        return jsonify({'result': 'success', 'token': token})
        # 일치하는 아이디와 비밀번호를 찾지 못하면
    else:
        return jsonify({'result':'fail', 'msg':'아이디 또는 비밀번호가 일치하지 않습니다.'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
