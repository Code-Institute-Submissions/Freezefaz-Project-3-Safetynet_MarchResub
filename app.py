from flask import Flask, render_template, request, redirect, url_for
import os
import pymongo
import dnspython
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

MONGO_URI = os.environ.get('MONGO_URI')
DB_NAME = "safetynet"
client = pymongo.MongoClient(MONGO_URI)

# "magic code" -- boilerplate
if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
