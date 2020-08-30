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

MONGO_URI = os.environ.get('MONGO_URI')
SECRET_KEY = os.environ.get('SECRET_KEY')
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
    password = request.form.get("password")

    # Accumulator to capture errors
    errors = {}

    # check if information is valid
    # the order of conditions matter in app and html as well

    if first_name == "" or first_name == " ":
        errors.update(
            first_name_empty="Please enter a name")

    # Check if the name is made up of alphabets
    if not first_name.isalpha():
        errors.update(
            first_name_not_letter="Please enter a letter")

    # check if the first_name is longer 3 characters
    if len(first_name) < 3:
        errors.update(
            first_name_too_short="Must be at least 2 letters")

    if last_name == "" or last_name == " ":
        errors.update(
            last_name_empty="Please enter a name")

    # Check if the name is made up of alphabets
    if not last_name.isalpha():
        errors.update(
            last_name_not_letter="Please enter a letter")

    # check if the last_name is longer 2 characters
    if len(last_name) < 3:
        errors.update(
            last_name_too_short="Must be at least 2 letters")

    if contact_number == "" or contact_number == " ":
        errors.update(
            contact_number_empty="Please enter a contact_number")

    # contact number must be number
    if not contact_number.isnumeric():
        errors.update(
            contact_number_not_a_number="Please enter a number")

     # check if the contact_number is 8 characters
    if not len(contact_number) == 8:
        errors.update(
            contact_number_must_be_8="Must be 8 numbers long")

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
        # flash("Unable to add Safety Officer", "danger")
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
    # flash("New Safety Officer Added", "success")
    return redirect(url_for("show_officers"))


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
        # flash("Unable to add Safety Officer", "danger")
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
        return redirect(url_for("index"))

    # if login failed, return back to login page
    else:
        return redirect(url_for("login"))


@app.route("/officers/logout")
def logout():
    flask_login.logout_user()
    return redirect(url_for("index"))


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

    # Check if the name is made up of alphabets
    if not first_name.isalpha():
        errors.update(
            first_name_not_letter="Please enter a letter")

    # check if the first_name is longer 3 characters
    if len(first_name) < 3:
        errors.update(
            first_name_too_short="Must be at least 2 letters")

    if last_name == "" or last_name == " ":
        errors.update(
            last_name_empty="Please enter a name")

    # Check if the name is made up of alphabets
    if not last_name.isalpha():
        errors.update(
            last_name_not_letter="Please enter a letter")

    # check if the last_name is longer 2 characters
    if len(last_name) < 3:
        errors.update(
            last_name_too_short="Must be at least 2 letters")

    if contact_number == "" or contact_number == " ":
        errors.update(
            contact_number_empty="Please enter a contact_number")

    # contact number must be number
    if not contact_number.isnumeric():
        errors.update(
            contact_number_not_a_number="Please enter a number")

     # check if the contact_number is 8 characters
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

# ACCIDENT REPORT
@app.route("/accident_reports")
def show_accident_reports():
    all_accident_reports = db.accident_reports.find()
    return render_template("show_accident_reports.template.html",
                           accident_reports=all_accident_reports)

@app.route("/accident_reports/create")
@flask_login.login_required
def show_create_accident_report():
    accident_types = db.accident_types.find()
    safety_officers = db.safety_officers.find()

    # if flask_login.current_user.is_authenticated:
    #     current_user = flask_login.current_user

    #     if current_user:
    #         user = db.safety_officers.find_one({'email': email})
    #     else:
    #         user = none
    # else:
    #     return redirect(url_for('index'))

    return render_template("create_accident_reports.template.html", errors={},
                           accident_types=accident_types,
                           safety_officers=safety_officers)


@app.route("/accident_reports/create", methods=["Post"])
# @flask_login.login_required
def process_create_accident_report():
    # extract info from forms
    date = request.form.get("date")
    location = request.form.get("location")
    accident_type_id = request.form.get("accident_type")
    description = request.form.get("description")
    injuries = request.form.get("injuries")
    safety_officer_id = request.form.get("safety_officer")

    # # get existing collection info
    # accident_type = db.accident_types.find_one({
    #     "_id": ObjectId(accident_type_id)
    # })
    # safety_officer = db.safety_officers.find_one({
    #     "_id": ObjectId(safety_officer_id)
    # })

    # Validation
    # Accumulator to capture errors
    errors = {}

    # check if information is valid
    # the order of conditions matter in app and html as well

    # Check if the date in numbers
    if date == "" or date == " ":
        errors.update(
            date_empty="Please enter a date")

    # check if the date in correct format
    # if not date.isnumeric():
    #     errors.update(
    #         date_wrong_format = "Please enter Date in YYYY-MM-DD")

    if location == "" or location == " ":
        errors.update(
            location_empty="Please enter a location")

    if len(location) < 3:
        errors.update(
            location_too_short="Please enter at least 3 characters")

    # Check if location no more than 50 characters
    if not len(location) <= 50:
        errors.update(
            location_too_long="Please keep to 50 characters")

    if description == "" or description == " ":
        errors.update(
            description_empty="Please enter a description")

    if len(description) < 3:
        errors.update(
            description_too_short="Please enter at least 3 characters")

    # Check if description no more than 255 characters
    if not len(description) <= 255:
        errors.update(
            description_too_long="Please keep to 255 characters")

    if injuries == "" or injuries == " ":
        errors.update(
            injuries_empty="Please enter an injury")

    if len(injuries) < 3:
        errors.update(
            injuries_too_short="Please enter at least 3 characters")

    # Check if injuries no more than 50 characters
    if not len(injuries) <= 50:
        errors.update(
            injuries_too_long="Please keep to 50 characters")

    # if errors go back to form and try again
    if len(errors) > 0:
        # Do this so that when the select will repopulate
        accident_types = db.accident_types.find()
        safety_officers = db.safety_officers.find()
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
        # "accident_type": accident_type,
        "accident_type": accident_type["accident_type"],
        "accident_type_id": ObjectId(accident_type_id),
        "description": description,
        "injuries": injuries,
        "safety_officer": safety_officer["first_name"] + " "
        + safety_officer["last_name"],
        "safety_officer_id": ObjectId(safety_officer_id)
        # "safety_officer": safety_officer

    }

    # Add the query to the database and the front page
    db.accident_reports.insert_one(new_accident_report)
    return redirect(url_for("show_accident_reports"))

# Update accident report


@app.route("/accident_reports/update/<accident_report_id>")
# @flask_login.login_required
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


@app.route("/accident_reports/update/<accident_report_id>", methods=["POST"])
def process_update_accident_report(accident_report_id):
    date = request.form.get("date")
    location = request.form.get("location")
    accident_type_id = request.form.get("accident_type")
    description = request.form.get("description")
    injuries = request.form.get("injuries")
    safety_officer_id = request.form.get("safety_officer")

    errors = {}

    if location == "" or location == " ":
        errors.update(
            location_empty="Please enter a location")

    if len(location) < 3:
        errors.update(
            location_too_short="Please enter at least 3 characters")

    # Check if location no more than 50 characters
    if not len(location) <= 50:
        errors.update(
            location_too_long="Please keep to 50 characters")

    if description == "" or description == " ":
        errors.update(
            description_empty="Please enter a description")

    if len(description) < 3:
        errors.update(
            description_too_short="Please enter at least 3 characters")

    # Check if description no more than 255 characters
    if not len(description) <= 255:
        errors.update(
            description_too_long="Please keep to 255 characters")

    if injuries == "" or injuries == " ":
        errors.update(
            injuries_empty="Please enter an injury")

    if len(injuries) < 3:
        errors.update(
            injuries_too_short="Please enter at least 3 characters")

    # Check if injuries no more than 50 characters
    if not len(injuries) <= 50:
        errors.update(
            injuries_too_long="Please keep to 50 characters")

    # if errors go back to form and try again
    if len(errors) > 0:
        # Do this so that when the select will repopulate
        accident_types = db.accident_types.find()
        safety_officers = db.safety_officers.find()
        return render_template("create_accident_reports.template.html",
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
            "safety_officer_id": ObjectId(safety_officer_id)
        }
    })

    return redirect(url_for("show_accident_reports",
                            accident_report_id=accident_report_id))

# Deleting accident report


@app.route("/accident_reports/delete/<accident_report_id>")
# @flask_login.login_required
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
    return redirect(url_for("show_accident_reports"))

# NEAR MISS
@app.route("/near_miss_reports")
def show_near_miss_reports():
    all_near_miss_reports = db.near_miss_reports.find()
    return render_template("show_near_miss_reports.template.html",
                           near_miss_reports=all_near_miss_reports)


@app.route("/near_miss_reports/create")
# @flask_login.login_required
def show_create_near_miss_report():
    safety_officers = db.safety_officers.find()
    return render_template("create_near_miss_report.template.html", errors={},
                           safety_officers=safety_officers)


@app.route("/near_miss_reports/create", methods=["Post"])
# @flask_login.login_required
def process_create_near_miss_accident_report():
    # extract info from forms
    date = request.form.get("date")
    location = request.form.get("location")
    description = request.form.get("description")
    safety_officer_id = request.form.get("safety_officer")

    # Validation
    # Accumulator to capture errors
    errors = {}

    # check if information is valid
    # the order of conditions matter in app and html as well

    # Check if the date in numbers
    if date == "" or date == " ":
        errors.update(
            date_empty="Please enter a date")

    # check if the date in correct format
    if not date.isnumeric():
        errors.update(
            date_wrong_format="Please enter Date in YYYY-MM-DD")

    if location == "" or location == " ":
        errors.update(
            location_empty="Please enter a location")

    if len(location) < 3:
        errors.update(
            location_too_short="Please enter at least 3 characters")

    # # Check if location no more than 50 characters
    if not len(location) <= 50:
        errors.update(
            location_too_long="Please keep to 50 characters")

    if description == "" or description == " ":
        errors.update(
            description_empty="Please enter a description")

    if len(description) < 3:
        errors.update(
            description_too_short="Please enter at least 3 characters")

    # # Check if description no more than 255 characters
    if not len(description) <= 255:
        errors.update(
            description_too_long="Please keep to 255 characters")

    # if errors go back to form and try again
    if len(errors) > 0:
        # Do this so that when the select will repopulate
        safety_officers = db.safety_officers.find()
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
        "safety_officer_id": ObjectId(safety_officer_id)
    }

    # Add the query to the database and the front page
    db.near_miss_reports.insert_one(new_near_miss_report)
    return redirect(url_for("show_near_miss_reports"))

@app.route("/near_miss_reports/update/<near_miss_report_id>")
def show_update_near_miss_report(near_miss_report_id):
    near_miss_report = db.near_miss_reports.find_one({
        "_id": ObjectId(near_miss_report_id)
    })
    safety_officers = db.safety_officers.find()
    return render_template("update_near_miss_report.template.html",
                           near_miss_report=near_miss_report,
                           safety_officers=safety_officers)

@app.route("/near_miss_reports/update/<near_miss_report_id>", methods=["POST"])
def process_update_near_miss_report(near_miss_report_id):
    date = request.form.get("date")
    location = request.form.get("location")
    description = request.form.get("description")
    safety_officer_id = request.form.get("safety_officer")

    errors = {}

    # Check if the date in numbers
    if date == "" or date == " ":
        errors.update(
            date_empty="Please enter a date")

    if location == "" or location == " ":
        errors.update(
            location_empty="Please enter a location")

    if len(location) < 3:
        errors.update(
            location_too_short="Please enter at least 3 characters")

    # Check if location no more than 50 characters
    if not len(location) <= 50:
        errors.update(
            location_too_long="Please keep to 50 characters")

    if description == "" or description == " ":
        errors.update(
            description_empty="Please enter a description")

    if len(description) < 3:
        errors.update(
            description_too_short="Please enter at least 3 characters")

    # Check if description no more than 255 characters
    if not len(description) <= 255:
        errors.update(
            description_too_long="Please keep to 255 characters")

    # if errors go back to form and try again
    if len(errors) > 0:
        # Do this so that when the select will repopulate
        safety_officers = db.safety_officers.find()
        return render_template("create_near_miss_report.template.html",
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
            "safety_officer_id": ObjectId(safety_officer_id)
        }
    })

    return redirect(url_for("show_near_miss_reports",
                            near_miss_report_id=near_miss_report_id))

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
    return redirect(url_for("show_near_miss_reports"))

# VIOLATIONS
@app.route("/violation_reports")
def show_violation_reports():
    all_violation_reports = db.violation_reports.find()
    return render_template("show_violation_reports.template.html",
                           violation_reports=all_violation_reports)


@app.route("/violation_reports/create")
@flask_login.login_required
def show_create_violation_report():
    violation_types = db.violation_types.find()
    safety_officers = db.safety_officers.find()

    return render_template("create_violation_report.template.html", errors={},
                           violation_types=violation_types,
                           safety_officers=safety_officers)

@app.route("/violation_reports/create", methods=["Post"])
def process_create_violation_report():
    # extract info from forms
    date = request.form.get("date")
    location = request.form.get("location")
    violation_type_id = request.form.get("violation_type")
    description = request.form.get("description")
    safety_officer_id = request.form.get("safety_officer")

    # Validation
    # Accumulator to capture errors
    errors = {}

    # check if information is valid
    # the order of conditions matter in app and html as well

    # Check if the date in numbers
    if date == "" or date == " ":
        errors.update(
            date_empty="Please enter a date")

    if location == "" or location == " ":
        errors.update(
            location_empty="Please enter a location")

    if len(location) < 3:
        errors.update(
            location_too_short="Please enter at least 3 characters")

    # Check if location no more than 50 characters
    if not len(location) <= 50:
        errors.update(
            location_too_long="Please keep to 50 characters")

    if description == "" or description == " ":
        errors.update(
            description_empty="Please enter a description")

    if len(description) < 3:
        errors.update(
            description_too_short="Please enter at least 3 characters")

    # Check if description no more than 255 characters
    if not len(description) <= 255:
        errors.update(
            description_too_long="Please keep to 255 characters")

    # if errors go back to form and try again
    if len(errors) > 0:
        # Do this so that when the select will repopulate
        violation_types = db.violation_types.find()
        safety_officers = db.safety_officers.find()
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
        "safety_officer_id": ObjectId(safety_officer_id)
    }
    # Add the query to the database and the front page
    db.violation_reports.insert_one(new_violation_report)
    return redirect(url_for("show_violation_reports"))

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
                           safety_officers=safety_officers)

@app.route("/violation_reports/update/<violation_report_id>", methods=["POST"])
def process_update_violation_report(violation_report_id):
    date = request.form.get("date")
    location = request.form.get("location")
    violation_type_id = request.form.get("violation_type")
    description = request.form.get("description")
    safety_officer_id = request.form.get("safety_officer")

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

    # Check if location no more than 50 characters
    if not len(location) <= 50:
        errors.update(
            location_too_long="Please keep to 50 characters")

    if description == "" or description == " ":
        errors.update(
            description_empty="Please enter a description")

    if len(description) < 3:
        errors.update(
            description_too_short="Please enter at least 3 characters")

    # Check if description no more than 255 characters
    if not len(description) <= 255:
        errors.update(
            description_too_long="Please keep to 255 characters")

    # if errors go back to form and try again
    if len(errors) > 0:
        # Do this so that when the select will repopulate
        violation_types = db.violation_types.find()
        safety_officers = db.safety_officers.find()
        return render_template("create_violation_report.template.html",
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
            "safety_officer_id": ObjectId(safety_officer_id)
        }
    })

    return redirect(url_for("show_violation_reports",
                            violation_report_id=violation_report_id))

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
    return redirect(url_for("show_violation_reports"))


# "magic code" -- boilerplate
if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
