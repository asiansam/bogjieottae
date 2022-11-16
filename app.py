import dotenv
import os
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from pymongo import MongoClient
from datetime import datetime, timedelta
import certifi
import jwt
import hashlib

dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

ca = certifi.where()
client = MongoClient(os.environ["mongDB"],tlsCAFile=ca)

db = client.bogjieottae

app = Flask(__name__)
FILE_PATH = f"static/img/"

SECRET_KEY = 'SPARTA'


@app.route('/')
def home():
    return render_template('login.html')



@app.route('/login')
def login():
    msg = request.args.get("msg")

    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"id": payload['id']})
        return render_template('index.html', nickname=user_info["nick"])
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/api/register', methods=['POST'])
def api_register():
    ## 웹에서 계정정보를 받아 와요
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    nickname_receive = str(request.form['nickname_give'])
    print(request.form)
    ## 아이디 조회/닉네임 조회부터 할께요!
    print(db.user.find_one({'id':id_receive}, {'_id': False}))
    idList = db.user.find_one({'id':id_receive}, {'_id': False})
    nickList = db.user.find_one({'nick':nickname_receive}, {'_id': False})

    if( idList != None):
        return jsonify({'result': '중복된 아이디 입니다.'})
    elif(nickList != None):
        return jsonify({'result': '중복된 닉네임 입니다.'})
    else:
        pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
        db.user.insert_one({'id': id_receive, 'pw': pw_hash, 'nick': nickname_receive , 'is_saved':[]})

        return jsonify({'result': 'success'})
@app.route('/api/login', methods=['POST'])
def api_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    result = db.user.find_one({'id': id_receive, 'pw': pw_hash})
    print(id_receive)

    if result is not None:

        payload = {
            'id': id_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

@app.route('/api/nick', methods=['GET'])
def api_valid():
    token_receive = request.cookies.get('mytoken')
    try:

        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        print(payload)

        userinfo = db.user.find_one({'id': payload['id']}, {'_id': 0})
        return jsonify({'result': 'success', 'nickname': userinfo['nick']})
    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})

@app.route('/createcompany')
def view_create_company():
    return render_template('createCompany.html')

@app.route('/profile')
def view_profile_Page():
    return render_template('MyProfile.html')

@app.route('/detail',methods=["GET"])
def view_company_detail():
    return render_template('companyDetail.html')

@app.route('/main')
def view_main_Page():
    return render_template('mainPage.html')


@app.route('/api/deleteComment',methods=["DELETE"])
def delete_comment():
    try:
        #현재 접속한 사용자
        token_receive = request.cookies.get('mytoken')
        user = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        #
        userinfo = db.user.find_one({'id': user['id']}, {'_id': 0})
        print("찾은유저는!!!",userinfo)

        find_comment = list(db.comment.find({"commentNumber": int(request.form["commentNumber"]), "companyName": request.form["companyName"], "user":userinfo["nick"]},{'_id':False}))
        if(len(find_comment) > 0):
            db.comment.delete_one({"commentNumber": int(request.form["commentNumber"]),"companyName":request.form["companyName"]})
            return jsonify({'msg': 'successfully!'})
        else:
            return jsonify({'msg': '본인 댓글만 삭제할 수 있습니다!'})
    except:
        print("Error")
@app.route('/api/getComment')
def get_comment():
    try:
        company_name = request.args.get("company")
        company_search = db.comment.find({"companyName":company_name},{'_id':False})
        req = list(company_search)
        return jsonify({"comment":req})
    except:
        print("Error~~~")

@app.route('/api/inputComment',methods=["POST"])
def post_comment():
    try:
        '''
        commentNumber = "번호"
        commentDate = "날짜"
        comment = "댓글 내용"
        companyName = "회사명"
        companyType = "유저명"
        '''
        commentList = list(db.comment.find({"companyName":request.form["companyName"]},{'_id':False}))

        if(len(commentList) > 0):
            count = commentList[-1]['commentNumber'] + 1
        else:
            count = 1


        doc = {
            "commentNumber":count,
            "commentDate":request.form["date"],
            "comment":request.form["comment"],
            "companyName":request.form["companyName"],
            "user":request.form["user"]
        }
        db.comment.insert_one(doc)
        print(list(db.comment.find({},{'_id':False})))
        return jsonify({'msg': 'successfully!'})
    except:
        print("ERROR")

@app.route("/api/profile", methods=["GET"])
def profile_get():
    company_list = list(db.company.find({}, {'_id': False}))

    return jsonify({'company':company_list})

@app.route('/api/detail',methods=["GET"])
def get_detail_company():
    try:
        company_name = request.args.get("company")
        company_search = db.company.find({"companyName":company_name},{'_id':False})
        req = list(company_search)
        req[0]['companyLogo'] = FILE_PATH + req[0]['companyLogo']
        return jsonify({"company_detail":req[0]})
    except:
        print("ERROR")

@app.route('/api/createcompany',methods=["POST"])
def create_company_poast():
    """
    회사 복지 등록

    몽고 DB에 저장될 값
    게시물 번호: 1
    회사이름: request.form['companyName'],
    회사내용: request.form['companyInfo'],
    사진경로: ,
    """
    #사진이 없을 경우 기본 경로 지정
    file_name = f"default.png"

    #파일이 있는지 체크
    if len(request.files.keys()) > 0:
        # 파일 저장을 위한 부분
        file = request.files['companyLogo']
        # 파일 확장자 분리
        extension = file.filename.split('.')[-1]
        today = datetime.now()
        time = today.strftime('%Y-%m-%d-%H-%M-%S')

        #이미지 파일명 생성
        file_name = f'file-{time}.{extension}'

        file_path = FILE_PATH + file_name
        #이미지 파일 저장
        file.save(file_path)

    #DB의 회사 개수 가져오기
    compnay_list = list(db.company.find({},{'_id':False}))
    count = len(compnay_list)

    #게시물 번호
    company_number = count + 1

    #회사이름
    company_name = request.form['companyName']

    #회사정보
    company_info = request.form['companyInfo']

    ##DB저장
    doc = {
        'companyNumber': company_number,
        'companyName': company_name,
        'companyInfo': company_info,
        'companyLogo': file_name,
    }
    db.company.insert_one(doc)
    print(list(db.company.find({},{'_id':False})))

    return jsonify({'msg': 'successfully!'})

@app.route("/api/mainpage", methods=["GET"])
def url_get():
    token_receive = request.cookies.get('mytoken')

    try:

        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        print(payload)
        company_list = list(db.company.find({}, {'_id': False}))

        # payload 안에 id가 들어있습니다. 이 id로 유저정보를 찾습니다.
        # 여기에선 그 예로 닉네임을 보내주겠습니다.
        userinfo = db.user.find_one({'id': payload['id']}, {'_id': 0})
        return jsonify({'result': 'success', 'user': userinfo,'company':company_list})
    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})

@app.route("/api/LIKE", methods=["POST"])
def comnum_post():
    num_receive = request.form["comnum_give"]

    token_receive = request.cookies.get('mytoken')

    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])


    userinfo = db.user.find_one({'id': payload['id']}, {'_id': 0})



    numarr = list(userinfo['is_saved'])

    print(numarr, payload)

    numarr.append(num_receive)

    db.user.update_one({'id': payload['id']}, {'$set':{'is_saved':numarr}})

    return jsonify({'msg': '좋아요!'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)