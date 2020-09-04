from flask import Flask, render_template, request, redirect, url_for, flash
import os
import flask_login
import pymongo
from dotenv import load_dotenv
from bson.objectid import ObjectId
import datetime
from passlib.hash import pbkdf2_sha256

load_dotenv()

app = Flask(__name__)

# variables from .env
MONGO_URI = os.environ.get('MONGO_URI')
SECRET_KEY = os.environ.get('SECRET_KEY')
CLOUD_NAME = os.environ.get('CLOUD_NAME')
UPLOAD_PRESET = os.environ.get('UPLOAD_PRESET')

# set up the secret key to flask app
app.secret_key = SECRET_KEY
DB_NAME = 'safetynet'
client = pymongo.MongoClient(MONGO_URI)
db = client[DB_NAME]


class User(flask_login.UserMixin):
    pass


# init the flask-login for app
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.init_view = 'login'


@login_manager.user_loader
def user_loader(email):
    user = db.safety_officers.find_one({
        'email': email
    })
    # if the email exists
    if user:
        # create a user object that represents user
        user_object = User()
        user_object.id = user["email"]
        # return user_object
        return user_object
    else:
        # if the email does not exist in the database. report an error
        return None

# Home Page
@app.route("/")
def index():
    return render_template("index.template.html")

# Start of officers

# show all officers
@app.route("/officers")
def show_officers():
    all_officers = db.safety_officers.find()
    return redirect(url_for("officers_search"))

#search officer by name
@app.route("/officers/search")
def officers_search():
    required_safety_officer_name = request.args.get("name") or ''
    criteria = {}

    if required_safety_officer_name:
        criteria["$or"] = [
            {
                "first_name": {
                    "$regex": required_safety_officer_name,
                    "$options": "i"
                }
            },
            {
                "last_name": {
                    "$regex": required_safety_officer_name,
                    "$options": "i"
                }}
        ]
    officers = db.safety_officers.find(criteria)
    return render_template("search_officers.template.html",
                           officers=officers,
                           required_safety_officer_name=required_safety_officer_name)

# register as an officer
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
    password = request.form.get("password")

    # Accumulator to capture errors
    errors = {}

    # check if information is valid
    # the order of conditions matter in app and html as well

    # Check if blank
    if first_name == "" or first_name == " ":
        errors.update(
            first_name_empty="Please enter a name")

    # Check if the name is made up of alphabets
    if not first_name.isalpha():
        errors.update(
            first_name_not_letter="Please enter a letter")

    # Check if the first_name is longer 3 characters
    if len(first_name) < 3:
        errors.update(
            first_name_too_short="Must be at least 2 letters")

    # Check if blank
    if last_name == "" or last_name == " ":
        errors.update(
            last_name_empty="Please enter a name")

    # Check if the name is made up of alphabets
    if not last_name.isalpha():
        errors.update(
            last_name_not_letter="Please enter a letter")

    # Check if the last_name is longer 2 characters
    if len(last_name) < 3:
        errors.update(
            last_name_too_short="Must be at least 2 letters")

    # Check if blank
    if contact_number == "" or contact_number == " ":
        errors.update(
            contact_number_empty="Please enter a contact_number")

    # Contact number must be number
    if not contact_number.isnumeric():
        errors.update(
            contact_number_not_a_number="Please enter a number")

     # Check if the contact_number is 8 characters
    if not len(contact_number) == 8:
        errors.update(
            contact_number_must_be_8="Must be 8 numbers long")

    # Check if blank
    if email == "" or email == " ":
        errors.update(
            email_empty="Please enter an email")

    if "@" not in email or "." not in email:
        errors.update(
            proper_email="Please enter a valid email")

    if not len(password) == 6:
        errors.update(
            password_too_short="Password needs to be 6 characters")

    # if errors go back to form and try again
    if len(errors) > 0:
        flash("Unable to add Safety Officer", "danger")
        return render_template("create_officers.template.html",
                               errors=errors,
                               previous_values=request.form)

    # create the query
    new_officer = {
        "first_name": first_name,
        "last_name": last_name,
        "contact_number": contact_number,
        "email": email,
        'password': password
    }

    # Add the query to the database and the front page
    db.safety_officers.insert_one(new_officer)
    flash("New Safety Officer Added", "success")
    return redirect(url_for("login"))

# officer to login
@app.route('/officers/login')
def login():
    return render_template("login.template.html")

@app.route('/officers/login', methods=["POST"])
def process_login():

    # retrieve the email and the password from the form
    email = request.form.get("email")
    password = request.form.get("password")

    # Accumulator to capture errors
    errors = {}

    if email == "" or email == " ":
        errors.update(
            email_empty="Please enter an email")

    if "@" not in email or "." not in email:
        errors.update(
            proper_email="Please enter a valid email")

    if password == "" or password == " ":
        errors.update(
            password_empty="Please enter an email")

    if not len(password) == 6:
        errors.update(
            password_too_short="Password needs to be 6 characters")

    # if errors go back to form and try again
    if len(errors) > 0:
        flash("Log in failed", "danger")
        return render_template("login.template.html",
                               errors=errors,
                               previous_values=request.form)

    # check if the user's email exist in the database
    user = db.safety_officers.find_one({
        'email': email
    })
    # if the user exist, check if the password matches
    if user and user["password"] == password:
        # if the password matches, authorize the user
        user_object = User()
        user_object.id = user["email"]
        # user_object.email = user["email"]
        flask_login.login_user(user_object)
        # redirect to the successful login page
        flash("Welcome!", "success")
        return redirect(url_for("officers_search"))
        
    # if login failed, return back to login page
    else:
        flash("Log in failed", "danger")
        return redirect(url_for("login"))

# logout from program
@app.route("/officers/logout")
def logout():
    flask_login.logout_user()
    flash("Thank You!", "success")
    return redirect(url_for("index"))

# update officer
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

    safety_officer = db.safety_officers.find_one({
        "_id": ObjectId(officer_id)
    })

    # Validation
    # Accumulator to capture errors
    errors = {}

    # check if information is valid
    # the order of conditions matter in app and html as well

    if first_name == "" or first_name == " ":
        errors.update(
            first_name_empty="Please enter a name")

    if not first_name.isalpha():
        errors.update(
            first_name_not_letter="Please enter a letter")

    if len(first_name) < 3:
        errors.update(
            first_name_too_short="Must be at least 2 letters")

    if last_name == "" or last_name == " ":
        errors.update(
            last_name_empty="Please enter a name")

    if not last_name.isalpha():
        errors.update(
            last_name_not_letter="Please enter a letter")

    if len(last_name) < 3:
        errors.update(
            last_name_too_short="Must be at least 2 letters")

    if contact_number == "" or contact_number == " ":
        errors.update(
            contact_number_empty="Please enter a contact_number")

    if not contact_number.isnumeric():
        errors.update(
            contact_number_not_a_number="Please enter a number")

    if not len(contact_number) == 8:
        errors.update(
            contact_number_must_be_8="Must be 8 numbers long")

    if email == "" or email == " ":
        errors.update(
            email_empty="Please enter an email")

    if "@" not in email or "." not in email:
        errors.update(
            proper_email="Please enter a valid email")

    # if errors go back to form and try again
    if len(errors) > 0:
        flash("Update failed", "danger")
        return render_template("update_officers.template.html",
                               errors=errors,
                               previous_values=request.form,
                               safety_officer=safety_officer)

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
    flash("Update successful", "success")
    return redirect(url_for("officers_search",officer_id=officer_id))

# delete officer
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
    flash("Delete successful", "success")
    return redirect(url_for("officers_search"))
# end of officers


# Start of accident reports
# show all officers
@app.route("/accident_reports")
def show_accident_reports():
    all_accident_reports = db.accident_reports.find()
    # return render_template("show_accident_reports.template.html",
    #                        accident_reports=all_accident_reports)
    return redirect(url_for("accidents_search"))

# search accident report by category and global search
@app.route("/accident_reports/search")
def accidents_search():
    required_search_by = request.args.get("accident_search_by") or ''
    required_specific = request.args.get("accident_specific") or ''
    required_accident = request.args.get("accident") or ''
    criteria = {}

    # category search
    if required_search_by == "1":
        criteria["location"] = {
            '$regex': required_specific,
            '$options': 'i'
        }
    elif required_search_by == "2":
        criteria["accident_type"] = {
            '$regex': required_specific,
            '$options': 'i'
        }
    else:
        criteria["injuries"] = {
            '$regex': required_specific,
            '$options': 'i'
        }

    # global search
    if required_accident:
        criteria["$or"] = [
            {
                "date": {
                    "$regex": required_accident,
                    "$options": "i"
                }
            },
            {
                "location": {
                    "$regex": required_accident,
                    "$options": "i"
                }
            },
            {
                "accident_type": {
                    "$regex": required_accident,
                    "$options": "i"
                }
            },
            {
                "description": {
                    "$regex": required_accident,
                    "$options": "i"
                }
            },
            {
                "injuries": {
                    "$regex": required_accident,
                    "$options": "i"
                }
            },
            {
                "safety_officer": {
                    "$regex": required_accident,
                    "$options": "i"
                }
            },
        ]
    # find the base on criteria of search
    accident_reports = db.accident_reports.find(criteria)
    return render_template("search_accidents.template.html",
                           required_search_by=required_search_by,
                           required_specific=required_specific,
                           required_accident=required_accident,
                           accident_reports=accident_reports,
                           previous_values=required_search_by,
                           previous_search=required_specific)

# create new accident report
@app.route("/accident_reports/create")
@flask_login.login_required
def show_create_accident_report():
    accident_types = db.accident_types.find()
    safety_officers = db.safety_officers.find()

    return render_template("create_accident_reports.template.html", errors={},
                           accident_types=accident_types,
                           safety_officers=safety_officers,
                           cloud_name=CLOUD_NAME,
                           upload_preset=UPLOAD_PRESET)


@app.route("/accident_reports/create", methods=["Post"])
def process_create_accident_report():
    # extract info from forms
    date = request.form.get("date")
    location = request.form.get("location")
    accident_type_id = request.form.get("accident_type")
    description = request.form.get("description")
    injuries = request.form.get("injuries")
    safety_officer_id = request.form.get("safety_officer")
    image_url = request.form.get("uploaded-file-url")
    asset_id = request.form.get("asset-id")

    # Validation
    # Accumulator to capture errors
    errors = {}

    # check if information is valid
    # the order of conditions matter in app and html as well

    if date == "" or date == " ":
        errors.update(
            date_empty="Please enter a date")

    if location == "" or location == " ":
        errors.update(
            location_empty="Please enter a location")

    if len(location) < 3:
        errors.update(
            location_too_short="Please enter at least 3 characters")

    if not len(location) <= 50:
        errors.update(
            location_too_long="Please keep to 50 characters")

    if description == "" or description == " ":
        errors.update(
            description_empty="Please enter a description")

    if len(description) < 3:
        errors.update(
            description_too_short="Please enter at least 3 characters")

    if not len(description) <= 255:
        errors.update(
            description_too_long="Please keep to 255 characters")

    if injuries == "" or injuries == " ":
        errors.update(
            injuries_empty="Please enter an injury")

    if len(injuries) < 3:
        errors.update(
            injuries_too_short="Please enter at least 3 characters")

    if not len(injuries) <= 50:
        errors.update(
            injuries_too_long="Please keep to 50 characters")

    # if errors go back to form and try again
    if len(errors) > 0:
        # Do this so that when the select will repopulate
        accident_types = db.accident_types.find()
        safety_officers = db.safety_officers.find()
        flash("Failed to create accident report", "danger")
        return render_template("create_accident_reports.template.html",
                               errors=errors,
                               previous_values=request.form,
                               accident_types=accident_types,
                               safety_officers=safety_officers)

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
        "accident_type": accident_type["accident_type"],
        "accident_type_id": ObjectId(accident_type_id),
        "description": description,
        "injuries": injuries,
        "safety_officer": safety_officer["first_name"] + " "
        + safety_officer["last_name"],
        "safety_officer_id": ObjectId(safety_officer_id),
        'image_url': image_url,
        'asset_id': asset_id
    }
    # Add the query to the database and the front page
    db.accident_reports.insert_one(new_accident_report)
    flash("Accident report created", "success")
    return redirect(url_for("accidents_search"))

# Update accident report
@app.route("/accident_reports/update/<accident_report_id>")
def show_update_accident_report(accident_report_id):
    accident_report = db.accident_reports.find_one({
        "_id": ObjectId(accident_report_id)
    })
    accident_types = db.accident_types.find()
    safety_officers = db.safety_officers.find()
    return render_template("update_accident_report.template.html",
                           accident_report=accident_report,
                           accident_types=accident_types,
                           safety_officers=safety_officers,
                           cloud_name=CLOUD_NAME,
                           upload_preset=UPLOAD_PRESET)

@app.route("/accident_reports/update/<accident_report_id>", methods=["POST"])
def process_update_accident_report(accident_report_id):
    date = request.form.get("date")
    location = request.form.get("location")
    accident_type_id = request.form.get("accident_type")
    description = request.form.get("description")
    injuries = request.form.get("injuries")
    safety_officer_id = request.form.get("safety_officer")
    image_url = request.form.get("uploaded-file-url")
    asset_id = request.form.get("asset-id")

    errors = {}

    if location == "" or location == " ":
        errors.update(
            location_empty="Please enter a location")

    if len(location) < 3:
        errors.update(
            location_too_short="Please enter at least 3 characters")

    if not len(location) <= 50:
        errors.update(
            location_too_long="Please keep to 50 characters")

    if description == "" or description == " ":
        errors.update(
            description_empty="Please enter a description")

    if len(description) < 3:
        errors.update(
            description_too_short="Please enter at least 3 characters")

    if not len(description) <= 255:
        errors.update(
            description_too_long="Please keep to 255 characters")

    if injuries == "" or injuries == " ":
        errors.update(
            injuries_empty="Please enter an injury")

    if len(injuries) < 3:
        errors.update(
            injuries_too_short="Please enter at least 3 characters")

    if not len(injuries) <= 50:
        errors.update(
            injuries_too_long="Please keep to 50 characters")

    # if errors go back to form and try again
    if len(errors) > 0:
        # Do this so that when the select will repopulate
        accident_types = db.accident_types.find()
        safety_officers = db.safety_officers.find()
        accident_report = db.accident_reports.find_one({
        "_id": ObjectId(accident_report_id)
    })
        flash("Failed to update accident report", "danger")
        return render_template("update_accident_report.template.html",
                               accident_report=accident_report,
                               errors=errors,
                               previous_values=request.form,
                               accident_types=accident_types,
                               safety_officers=safety_officers)

    # get existing collection info and change cursor to dict
    accident_reports = db.accident_reports.find_one({
        "_id": ObjectId(accident_report_id)
    }, {
        "_id": 1
    })
    accident_types = db.accident_types.find_one({
        "_id": ObjectId(accident_type_id)
    }, {
        "accident_type": 1
    })
    safety_officers = db.safety_officers.find_one({
        "_id": ObjectId(safety_officer_id)
    }, {
        "first_name": 1,
        "last_name": 1
    })

    db.accident_reports.update_one({
        "_id": ObjectId(accident_report_id)
    }, {
        "$set": {
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "location": location,
            "accident_type": accident_types["accident_type"],
            "accident_type_id": ObjectId(accident_type_id),
            "description": description,
            "injuries": injuries,
            "safety_officer": safety_officers["first_name"] + " "
            + safety_officers["last_name"],
            "safety_officer_id": ObjectId(safety_officer_id),
            'image_url': image_url,
            'asset_id': asset_id
        }
    })
    flash("Accident report updated", "success")
    return redirect(url_for("accidents_search",
                            accident_report_id=accident_report_id))

# deleting accident report
@app.route("/accident_reports/delete/<accident_report_id>")
def show_delete_accident_report(accident_report_id):
    accident_report = db.accident_reports.find_one({
        "_id": ObjectId(accident_report_id)
    })

    return render_template("delete_accident_report.template.html",
                           accident_report=accident_report)


@app.route("/accident_reports/delete/<accident_report_id>", methods=["POST"])
def process_delete_accident_report(accident_report_id):
    db.accident_reports.remove({
        "_id": ObjectId(accident_report_id)
    })
    flash("Accident report deleted", "success")
    return redirect(url_for("accidents_search"))
# End of accident report

# Start of near miss
# show all near miss report
@app.route("/near_miss_reports")
def show_near_miss_reports():
    all_near_miss_reports = db.near_miss_reports.find()
    return redirect(url_for("near_miss_search"))

# Search by global and location
@app.route("/near_miss_reports/search")
def near_miss_search():
    required_location = request.args.get("location") or ''
    required_near_miss = request.args.get("near_miss") or ''
    criteria = {}
    # search by location
    criteria["location"] = {
            '$regex': required_location,
            '$options': 'i'
        }
    # global search
    if required_near_miss:
        criteria["$or"] = [
            {
                "date": {
                    "$regex": required_near_miss,
                    "$options": "i"
                }
            },
            {
                "location": {
                    "$regex": required_near_miss,
                    "$options": "i"
                }
            },
            {
                "description": {
                    "$regex": required_near_miss,
                    "$options": "i"
                }
            },
            {
                "safety_officer": {
                    "$regex": required_near_miss,
                    "$options": "i"
                }
            },
        ]
    # find by criteria
    near_miss_reports = db.near_miss_reports.find(criteria)
    return render_template("search_near_miss.template.html",
                           near_miss_reports=near_miss_reports,
                           required_near_miss=required_near_miss)

# create near miss report
@app.route("/near_miss_reports/create")
@flask_login.login_required
def show_create_near_miss_report():
    safety_officers = db.safety_officers.find()
    return render_template("create_near_miss_report.template.html", errors={},
                           safety_officers=safety_officers,
                           cloud_name=CLOUD_NAME,
                           upload_preset=UPLOAD_PRESET)

@app.route("/near_miss_reports/create", methods=["Post"])
def process_create_near_miss_accident_report():
    # extract info from forms
    date = request.form.get("date")
    location = request.form.get("location")
    description = request.form.get("description")
    safety_officer_id = request.form.get("safety_officer")
    image_url = request.form.get("uploaded-file-url")
    asset_id = request.form.get("asset-id")

    # Validation
    # Accumulator to capture errors
    errors = {}

    # check if information is valid
    # the order of conditions matter in app and html as well

    if date == "" or date == " ":
        errors.update(
            date_empty="Please enter a date")

    if not date.isnumeric():
        errors.update(
            date_wrong_format="Please enter Date in YYYY-MM-DD")

    if location == "" or location == " ":
        errors.update(
            location_empty="Please enter a location")

    if len(location) < 3:
        errors.update(
            location_too_short="Please enter at least 3 characters")

    if not len(location) <= 50:
        errors.update(
            location_too_long="Please keep to 50 characters")

    if description == "" or description == " ":
        errors.update(
            description_empty="Please enter a description")

    if len(description) < 3:
        errors.update(
            description_too_short="Please enter at least 3 characters")

    if not len(description) <= 255:
        errors.update(
            description_too_long="Please keep to 255 characters")

    # if errors go back to form and try again
    if len(errors) > 0:
        # Do this so that when the select will repopulate
        safety_officers = db.safety_officers.find()
        flash("Failed to create near miss report", "danger")
        return render_template("create_near_miss_report.template.html",
                               errors=errors,
                               previous_values=request.form,
                               safety_officers=safety_officers)

    # get existing collection info
    safety_officer = db.safety_officers.find_one({
        "_id": ObjectId(safety_officer_id)
    })

    # Create near miss report
    new_near_miss_report = {
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "location": location,
        "description": description,
        "safety_officer": safety_officer["first_name"] + " "
        + safety_officer["last_name"],
        "safety_officer_id": ObjectId(safety_officer_id),
        'image_url': image_url,
        'asset_id': asset_id
    }

    # Add the query to the database and the front page
    db.near_miss_reports.insert_one(new_near_miss_report)
    flash("Near miss report created", "success")
    return redirect(url_for("near_miss_search"))

# update near miss report
@app.route("/near_miss_reports/update/<near_miss_report_id>")
def show_update_near_miss_report(near_miss_report_id):
    near_miss_report = db.near_miss_reports.find_one({
        "_id": ObjectId(near_miss_report_id)
    })
    safety_officers = db.safety_officers.find()
    return render_template("update_near_miss_report.template.html",
                           near_miss_report=near_miss_report,
                           safety_officers=safety_officers,
                           cloud_name=CLOUD_NAME,
                           upload_preset=UPLOAD_PRESET)


@app.route("/near_miss_reports/update/<near_miss_report_id>", methods=["POST"])
def process_update_near_miss_report(near_miss_report_id):
    date = request.form.get("date")
    location = request.form.get("location")
    description = request.form.get("description")
    safety_officer_id = request.form.get("safety_officer")
    image_url = request.form.get("uploaded-file-url")
    asset_id = request.form.get("asset-id")

    errors = {}

    if date == "" or date == " ":
        errors.update(
            date_empty="Please enter a date")

    if location == "" or location == " ":
        errors.update(
            location_empty="Please enter a location")

    if len(location) < 3:
        errors.update(
            location_too_short="Please enter at least 3 characters")

    if not len(location) <= 50:
        errors.update(
            location_too_long="Please keep to 50 characters")

    if description == "" or description == " ":
        errors.update(
            description_empty="Please enter a description")

    if len(description) < 3:
        errors.update(
            description_too_short="Please enter at least 3 characters")

    if not len(description) <= 255:
        errors.update(
            description_too_long="Please keep to 255 characters")

    # if errors go back to form and try again
    if len(errors) > 0:
        # Do this so that when the select will repopulate
        safety_officers = db.safety_officers.find()
        near_miss_report = db.near_miss_reports.find_one({
            "_id": ObjectId(near_miss_report_id)
    })
        flash("Failed to update near miss report", "danger")
        return render_template("update_near_miss_report.template.html",
                               near_miss_report=near_miss_report,
                               errors=errors,
                               previous_values=request.form,
                               safety_officers=safety_officers)

    # get existing collection info and change cursor to dict
    near_miss_reports = db.near_miss_reports.find_one({
        "_id": ObjectId(near_miss_report_id)
    }, {
        "_id": 1
    })
    safety_officers = db.safety_officers.find_one({
        "_id": ObjectId(safety_officer_id)
    }, {
        "first_name": 1,
        "last_name": 1
    })

    db.near_miss_reports.update_one({
        "_id": ObjectId(near_miss_report_id)
    }, {
        "$set": {
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "location": location,
            "description": description,
            "safety_officer": safety_officers["first_name"] + " "
            + safety_officers["last_name"],
            "safety_officer_id": ObjectId(safety_officer_id),
            'image_url': image_url,
            'asset_id': asset_id
        }
    })
    flash("Near miss report updated", "success")
    return redirect(url_for("near_miss_search", near_miss_report_id=near_miss_report_id))

# delete near miss report
@app.route("/near_miss_reports/delete/<near_miss_report_id>")
def show_delete_near_miss_report(near_miss_report_id):
    near_miss_report = db.near_miss_reports.find_one({
        "_id": ObjectId(near_miss_report_id)
    })

    return render_template("delete_near_miss_report.template.html",
                           near_miss_report=near_miss_report)

@app.route("/near_miss_reports/delete/<near_miss_report_id>", methods=["POST"])
def process_delete_near_miss_report(near_miss_report_id):
    db.near_miss_reports.remove({
        "_id": ObjectId(near_miss_report_id)
    })
    flash("Near miss report deleted", "success")
    return redirect(url_for("near_miss_search"))
# End of near miss report

# Start of violation report
#show all violation report
@app.route("/violation_reports")
def show_violation_reports():
    all_violation_reports = db.violation_reports.find()
    return redirect(url_for("violation_search"))

# search violation by category and global
@app.route("/violation_reports/search")
def violation_search():
    required_search_by = request.args.get("violation_search_by") or ''
    required_specific = request.args.get("violation_specific") or ''
    required_violation = request.args.get("violation") or ''
    criteria = {}
    # category search
    if required_search_by == "1":
        criteria["location"] = {
            '$regex': required_specific,
            '$options': 'i'
        }
    else:
        criteria["violation_type"] = {
            '$regex': required_specific,
            '$options': 'i'
        }
    # global search
    if required_violation:
        criteria["$or"] = [
            {
                "date": {
                    "$regex": required_violation,
                    "$options": "i"
                }
            },
            {
                "location": {
                    "$regex": required_violation,
                    "$options": "i"
                }
            },
            {
                "violation_type": {
                    "$regex": required_violation,
                    "$options": "i"
                }
            },
            {
                "description": {
                    "$regex": required_violation,
                    "$options": "i"
                }
            },
            {
                "safety_officer": {
                    "$regex": required_violation,
                    "$options": "i"
                }
            },
        ]
    # find by criteria
    violation_reports = db.violation_reports.find(criteria)
    return render_template("search_violations.template.html",
                           required_search_by=required_search_by,
                           required_specific=required_specific,
                           violation_reports=violation_reports,
                           required_violation=required_violation,
                           previous_values=required_search_by)

# create violation report
@app.route("/violation_reports/create")
@flask_login.login_required
def show_create_violation_report():
    violation_types = db.violation_types.find()
    safety_officers = db.safety_officers.find()

    return render_template("create_violation_report.template.html", errors={},
                           violation_types=violation_types,
                           safety_officers=safety_officers,
                           cloud_name=CLOUD_NAME,
                           upload_preset=UPLOAD_PRESET)


@app.route("/violation_reports/create", methods=["Post"])
def process_create_violation_report():
    # extract info from forms
    date = request.form.get("date")
    location = request.form.get("location")
    violation_type_id = request.form.get("violation_type")
    description = request.form.get("description")
    safety_officer_id = request.form.get("safety_officer")
    image_url = request.form.get("uploaded-file-url")
    asset_id = request.form.get("asset-id")

    # Validation
    # Accumulator to capture errors
    errors = {}

    # check if information is valid
    # the order of conditions matter in app and html as well
    if date == "" or date == " ":
        errors.update(
            date_empty="Please enter a date")

    if location == "" or location == " ":
        errors.update(
            location_empty="Please enter a location")

    if len(location) < 3:
        errors.update(
            location_too_short="Please enter at least 3 characters")

    if not len(location) <= 50:
        errors.update(
            location_too_long="Please keep to 50 characters")

    if description == "" or description == " ":
        errors.update(
            description_empty="Please enter a description")

    if len(description) < 3:
        errors.update(
            description_too_short="Please enter at least 3 characters")

    if not len(description) <= 255:
        errors.update(
            description_too_long="Please keep to 255 characters")

    # if errors go back to form and try again
    if len(errors) > 0:
        # Do this so that when the select will repopulate
        violation_types = db.violation_types.find()
        safety_officers = db.safety_officers.find()
        flash("Failed to create violation report", "danger")
        return render_template("create_violation_report.template.html",
                               errors=errors,
                               previous_values=request.form,
                               violation_types=violation_types,
                               safety_officers=safety_officers)

    # get existing collection info
    violation_type = db.violation_types.find_one({
        "_id": ObjectId(violation_type_id)
    })
    safety_officer = db.safety_officers.find_one({
        "_id": ObjectId(safety_officer_id)
    })

    # Create violation report
    new_violation_report = {
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "location": location,
        "violation_type": violation_type["violation_type"],
        "violation_type_id": ObjectId(violation_type_id),
        "description": description,
        "safety_officer": safety_officer["first_name"] + " "
        + safety_officer["last_name"],
        "safety_officer_id": ObjectId(safety_officer_id),
        'image_url': image_url,
        'asset_id': asset_id
    }
    # Add the query to the database and the front page
    db.violation_reports.insert_one(new_violation_report)
    flash("Violation report created", "success")
    return redirect(url_for("violation_search"))

# update violation report
@app.route("/violation_reports/update/<violation_report_id>")
def show_update_violation_report(violation_report_id):
    violation_report = db.violation_reports.find_one({
        "_id": ObjectId(violation_report_id)
    })
    violation_types = db.violation_types.find()
    safety_officers = db.safety_officers.find()
    return render_template("update_violation_report.template.html",
                           violation_report=violation_report,
                           violation_types=violation_types,
                           safety_officers=safety_officers,
                           cloud_name=CLOUD_NAME,
                           upload_preset=UPLOAD_PRESET)

@app.route("/violation_reports/update/<violation_report_id>", methods=["POST"])
def process_update_violation_report(violation_report_id):
    date = request.form.get("date")
    location = request.form.get("location")
    violation_type_id = request.form.get("violation_type")
    description = request.form.get("description")
    safety_officer_id = request.form.get("safety_officer")
    image_url = request.form.get("uploaded-file-url")
    asset_id = request.form.get("asset-id")

    errors = {}

    if date == "" or date == " ":
        errors.update(
            date_empty="Please enter a date")

    if location == "" or location == " ":
        errors.update(
            location_empty="Please enter a location")

    if len(location) < 3:
        errors.update(
            location_too_short="Please enter at least 3 characters")

    if not len(location) <= 50:
        errors.update(
            location_too_long="Please keep to 50 characters")

    if description == "" or description == " ":
        errors.update(
            description_empty="Please enter a description")

    if len(description) < 3:
        errors.update(
            description_too_short="Please enter at least 3 characters")

    if not len(description) <= 255:
        errors.update(
            description_too_long="Please keep to 255 characters")

    # if errors go back to form and try again
    if len(errors) > 0:
        # Do this so that when the select will repopulate
        violation_types = db.violation_types.find()
        safety_officers = db.safety_officers.find()
        violation_report = db.violation_reports.find_one({
            "_id": ObjectId(violation_report_id)
    })
        flash("Failed to update violation report", "danger")
        return render_template("update_violation_report.template.html",
                               violation_report=violation_report,
                               errors=errors,
                               previous_values=request.form,
                               violation_types=violation_types,
                               safety_officers=safety_officers)

    # get existing collection info and change cursor to dict
    violation_reports = db.violation_reports.find_one({
        "_id": ObjectId(violation_report_id)
    }, {
        "_id": 1
    })
    violation_types = db.violation_types.find_one({
        "_id": ObjectId(violation_type_id)
    }, {
        "violation_type": 1
    })
    safety_officers = db.safety_officers.find_one({
        "_id": ObjectId(safety_officer_id)
    }, {
        "first_name": 1,
        "last_name": 1
    })
    db.violation_reports.update_one({
        "_id": ObjectId(violation_report_id)
    }, {
        "$set": {
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "location": location,
            "violation_type": violation_types["violation_type"],
            "violation_type_id": ObjectId(violation_type_id),
            "description": description,
            "safety_officer": safety_officers["first_name"] + " "
            + safety_officers["last_name"],
            "safety_officer_id": ObjectId(safety_officer_id),
            'image_url': image_url,
            'asset_id': asset_id
        }
    })
    flash("Violation report updated", "success")
    return redirect(url_for("violation_search", violation_report_id=violation_report_id))

# delete violation report
@app.route("/violation_reports/delete/<violation_report_id>")
def show_delete_violation_report(violation_report_id):
    violation_report = db.violation_reports.find_one({
        "_id": ObjectId(violation_report_id)
    })

    return render_template("delete_violation_report.template.html",
                           violation_report=violation_report)

@app.route("/violation_reports/delete/<violation_report_id>", methods=["POST"])
def process_delete_violation_report(violation_report_id):
    db.violation_reports.remove({
        "_id": ObjectId(violation_report_id)
    })
    flash("Violation report deleted", "success")
    return redirect(url_for("violation_search"))
# End of violation report

# "magic code" -- boilerplate
if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=False)
