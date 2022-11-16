import dotenv
import os
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import certifi

dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

ca = certifi.where()
client = MongoClient(os.environ["mongDB"],tlsCAFile=ca)

db = client.bogjieottae

app = Flask(__name__)
FILE_PATH = f"static/img/"
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/createcompany')
def view_create_company():
    return render_template('createCompany.html')

@app.route('/profile')
def view_profile_Page():
    return render_template('MyProfile.html')

@app.route('/detail',methods=["GET"])
def view_company_detail():
    return render_template('companyDetail.html')

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
    except:
        print("ERROR")

@app.route("/api/profile", methods=["GET"])
def url_get():
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

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)