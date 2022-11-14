import dotenv
import os
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
import certifi

dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

ca = certifi.where()
client = MongoClient(os.environ["mongDB"],tlsCAFile=ca)

db = client.dbsparta

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')


print(list(db.bucket.find({},{'_id':False})))