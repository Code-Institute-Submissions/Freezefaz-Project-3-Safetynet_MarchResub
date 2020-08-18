from flask import Flask, render_template, request, redirect, url_for
import os
import pymongo
from dotenv import load_dotenv
from bson.objectid import ObjectId
import datetime

load_dotenv()

app = Flask(__name__)

MONGO_URI = os.environ.get('MONGO_URI')
DB_NAME = 'safetynet'
client = pymongo.MongoClient(MONGO_URI)
db = client[DB_NAME]

@app.route('/officers')
def show_officers():
    all_officers = db.safety_officers.find()
    return render_template("show_officers.template.html", 
                            officers=all_officers)

@app.route('/officers/create')
def create_officers():
    return render_template("create_officers.template.html")

@app.route('/officers/create', methods=["POST"])
def process_create_officers():
    # process the form
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    contact_number = request.form.get("contact_number")
    email = request.form.get("email")
    # return render_template("create_officers.template.html",
    #                         first_name=first_name,
    #                         last_name=last_name,
    #                         contact_number=contact_number,
    #                         email=email)

    # create the query
    new_officer = {
        "first_name": first_name,
        "last_name": last_name,
        "contact_number": contact_number,
        "email": email
    }

    # Add the query to the database and the front page
    db.safety_officers.insert_one(new_officer)
    return redirect(url_for("show_officers"))

@app.route('/officers/update/<officer_id>')
def show_update_officer(officer_id):
    officer = db.safety_officers.find_one({
        '_id': ObjectId(officer_id)
    })
    return render_template('update_officers.template.html', officer=safety_officer)


# "magic code" -- boilerplate
if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
