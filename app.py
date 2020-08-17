from flask import Flask, render_template, request, redirect, url_for
import os
import pymongo
from dotenv import load_dotenv
import datetime

load_dotenv()

app = Flask(__name__)

MONGO_URI = os.environ.get('MONGO_URI')
DB_NAME = "safetynet"
client = pymongo.MongoClient(MONGO_URI)
db = client[DB_NAME]

@app.route("/officers")
def show_reports():
    all_officers = db.safety_officers.find()
    return render_template("show_reports.template.html", officers=all_officers)


# "magic code" -- boilerplate
if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
