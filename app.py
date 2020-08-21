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

@app.route("/")
def index():
    return render_template("index.template.html")

@app.route("/officers")
def show_officers():
    all_officers = db.safety_officers.find()
    return render_template("show_officers.template.html", 
                            officers=all_officers)

@app.route("/officers/create")
def create_officers():
    return render_template("create_officers.template.html", errors={})

@app.route("/officers/create", methods=["POST"])
def process_create_officers():
    # process the form
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    contact_number = request.form.get("contact_number")
    email = request.form.get("email")

    # # Accumulator to capture errors
    # errors = {}

    # # check if information is valid

    # # check if the first_name is longer 3 characters
    # if len(first_name) < 4:
    #     errors.update(
    #         first_name_too_short = "First Name must be 3 letters long")

    # if not first_name.isalpha():
    #     errors.update(
    #         first_name_not_letter = "Please enter a letter")

    # # check if the last_name is longer 2 characters
    # if len(last_name) < 3:
    #     errors.update(
    #         last_name_too_short = "Last Name must be 2 letters long")

    # if not first_name.isalpha():
    #     errors.update(
    #         last_name_not_letter = "Please enter a letter")

    #  # check if the contact_number is 8 characters
    # if len(contact_number) == 8:
    #     errors.update(
    #         contact_number_must_be_8 = "Must be 8 numbers long")

    # # contact number must be number
    # if not contact_number.isnumeric():
    #     errors.update(
    #         contact_number_not_a_number = "Please enter a number")

    # if "@" not in email:
    #     errors.update(
    #         proper_email = "Please enter a valid email")

    # # if errors go back to form and try again
    # if len(errors) > 0:
    #     return render_template("create_officers.template.html",
    #                             errors=errors,
    #                             previous_values=request.form)

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

@app.route("/officers/update/<officer_id>")
def show_update_officer(officer_id):
    safety_officer = db.safety_officers.find_one({
        "_id": ObjectId(officer_id)
    })
    return render_template("update_officers.template.html",
                            safety_officer=safety_officer)

@app.route("/officers/update/<officer_id>", methods=["POST"])
def process_update_officer(officer_id):

    # extract out info from forms
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    contact_number = request.form.get("contact_number")
    email = request.form.get("email")

    # Validation?

    # update safety officer
    db.safety_officers.update_one({
        '_id': ObjectId(officer_id)
    }, {
        '$set': {
            "first_name": first_name,
            "last_name": last_name,
            "contact_number": contact_number,
            "email": email
        }
    })

    return redirect(url_for('show_officers'))

@app.route("/officers/delete/<officer_id>")
def show_delete_officer(officer_id):
    safety_officer = db.safety_officers.find_one({
        "_id": ObjectId(officer_id)
    })
    return render_template("delete_officers.template.html",
                            safety_officer=safety_officer)

@app.route("/officers/delete/<officer_id>", methods=["POST"])
def process_delete_officer(officer_id):
    db.safety_officers.remove({
        "_id": ObjectId(officer_id)
    })
    return redirect(url_for("show_officers"))

   # Create accident report

@app.route("/accident_reports")
def show_accident_reports():
    all_accident_reports = db.accident_reports.find()
    return render_template("show_accident_reports.template.html",
                            accident_reports=all_accident_reports)

@app.route("/accident_reports/create")
def show_create_accident_report():
    accident_types = db.accident_types.find()
    safety_officers = db.safety_officers.find()
    return render_template("create_accident_reports.template.html", errors={},
                           accident_types=accident_types,
                           safety_officers=safety_officers)

@app.route("/accident_reports/create", methods=["Post"])
def process_create_accident_report():
    # extract info from forms
    date = request.form.get("date")
    location = request.form.get("location")
    accident_type_id = request.form.get("accident_type_id")
    description = request.form.get("description")
    injuries = request.form.get("injuries")
    safety_officer_id = request.form.get("safety_officer_id")

    # get existing collection info
    accident_type = db.accident_types.find_one({
        "_id": ObjectId(accident_type_id)
    })
    safety_officer = db.safety_officers.find_one({
        "_id": ObjectId(safety_officer_id)
    })

    # Create accident report
    new_accident_report = {
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "location": location,
        # "accident_type": accident_type["accident_type"],
        "accident_type": accident_type,
        # "accident_type_id": ObjectId(accident_type_id),
        "description": description,
        "injuries": injuries,
        # "safety_officer": safety_officer["first_name"] + " "
        # + safety_officer["last_name"],
        "safety_officer": safety_officer
        # "safety_officer_id": ObjectId(safety_officer_id)
    }

    # Add the query to the database and the front page
    db.accident_reports.insert_one(new_accident_report)
    return redirect(url_for("show_accident_reports"))

# Update accident report
@app.route("/accident_reports/<accident_report_id>/update")
def show_update_accident_report(accident_report_id):
    accident_report = db.accident_reports.find_one({
       "_id": ObjectId(accident_report_id)
    })
    accident_types = db.accident_types.find()
    safety_officers = db.safety_officers.find()
    return render_template("update_accident_report.template.html",
                           accident_report=accident_report,
                           accident_types=accident_types,
                           safety_officers=safety_officers)

@app.route("/accident_reports/<accident_report_id>/update", methods=["POST"])
def process_update_accident_report(accident_report_id):
    date = request.form.get("date")
    location = request.form.get("location")
    accident_type_id = request.form.get("accident_type_id")
    description = request.form.get("description")
    injuries = request.form.get("injuries")
    safety_officer_id = request.form.get("safety_officer_id")

    print(type(date))
    print(type(location))
    print(type(accident_type_id))
    print(type(description))
    print(type(injuries))
    print(type(safety_officer_id)) 
    

    # get existing collection info
    accident_report = db.accident_reports.find_one({
        "_id": ObjectId(accident_report_id)
    },{
        "_id": 1
    })
    accident_type = db.accident_types.find({
        "_id": ObjectId(accident_type_id)
    })
    safety_officer = db.safety_officers.find({
        "_id": ObjectId(safety_officer_id)
    })
    print("")
    print(type(accident_report))
    print(type(accident_type))
    print(type(safety_officer))

    db.accident_reports.update_one({
        "accident_report_id": ObjectId(accident_report_id)
    }, {
        "$set": {
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "location": location,
            "accident_type": accident_type,
            "description": description,
            "injuries": injuries,
            "safety_officer": safety_officer
        }
    })

    return redirect(url_for("show_accident_reports",
                            accident_report_id=accident_report["_id"]))





# "magic code" -- boilerplate
if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
