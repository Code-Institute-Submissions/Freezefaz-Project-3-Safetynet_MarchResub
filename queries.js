// To test queries before inserting to mongo
mongo "mongodb+srv://cluster0.uaguy.mongodb.net/" --username root

		<!-- <a class="navbar-brand"
			href="{{url_for ('index')}}"><img src="{{url_for('static', filename='image/logo.jpg')}}"></a> -->
// To populate safety officers

db.safety_officers.insert({
    "first_name": "Ahmed",
    "last_name": "Albab",
    "contact_number": "99991111",
    "email": "aa@safety.net"
})

db.safety_officers.insertMany([
    {
        "first_name": "Mike",
        "last_name": "Tan",
        "contact_number": "88882222",
        "email": "mt@safety.net"
    },
    {
        "first_name": "Velu",
        "last_name": "Kumar",
        "contact_number": "77773333",
        "email": "mt@safety.net"
    }
])

// To remove a guy

db.safety_officers.remove({
    "_id" : ObjectId("5f3a25122cde7c1882d3e0ab")
})


// Will modify existing safety officers with reports array
db.safety_officers.update({
    "_id" : ObjectId("5f3a25122cde7c1882d3e0ac")
},{
    "first_name": "Velu",
    "last_name": "Kumar",
    "contact_number": "77773333",
    "email": "mt@safety.net",
    "reports":[]
})

// will create a new entity 
db.safety_officers.insert({

        "first_name": "Mike",
        "last_name": "Tan",
        "contact_number": "88882222",
        "email": "mt@safety.net",
        "reports":[]
})

db.safety_officers.update({
    "_id" : ObjectId("5f3a25ab2cde7c1882d3e0ad")
},{
    "first_name": "Ahmed",
    "last_name": "Albab",
    "contact_number": "99991111",
    "email": "aa@safety.net",
     "reports":[]
})

// to insert a new element to array
db.safety_officers.update({
    "_id": ObjectId("5f3a25122cde7c1882d3e0ac")
},
{
    "$push": {
        "reports": {
            "_id": ObjectId(),
            "report_type": "Accident",
            "accident_type": "Electrical",
            "date": ISODate("2020-08-17"),
            "location": "Server Room",
            "description": "Worker electrocuted during electrical checks as wire not grounded",
            "injuries": "Hand burnt"
        }
    }
})

db.safety_officers.update({
    "_id": ObjectId("5f3a25ab2cde7c1882d3e0ad")
},
{
    "$push": {
        "reports": {
            "_id": ObjectId(),
            "report_type": "Near Miss",
            "date": ISODate("2020-08-16"),
            "location": "Warehouse",
            "description": "Box fell from forklift during lifting"
        }
    }
})

db.safety_officers.update({
    "_id": ObjectId("5f3a2f652cde7c1882d3e0b1")
},
{
    "$push": {
        "reports": {
            "_id": ObjectId(),
            "report_type": "Violation",
            "violation_type": "Scaffolding",
            "date": ISODate("2020-08-15"),
            "location": "foyer",
            "description": "Worker using scaffold despite OK tag expiring"
        }
    }
})

// Remove elements in an array
db.safety_officers.update({
    "_id":ObjectId("5f3a2f652cde7c1882d3e0b1")
}, {
    "$pull": {
        "reports": {
              "_id":ObjectId("5f3a38422cde7c1882d3e0b8")
        }
    }
})

// For reports
db.reports.insert({
            "report_type": "Accident",
            "accident_type": "Electrical",
            "date": ISODate("2020-08-17"),
            "location": "Server Room",
            "description": "Worker electrocuted during electrical checks as wire not grounded",
            "injuries": "Hand burnt"
})

Create report types

db.accident_types.insertMany([
    {
        "accident_type": "Cuts by object"
    },
    {
        "accident_type": "Electrical"
    },
    {
        "accident_type": "Fire or Explosion"
    },
    {
        "accident_type": "Pinched by object"
    },
    {
        "accident_type": "Slips, trips or falls"
    },
    {
        "accident_type": "Struck by object"
    },
    {
        "accident_type": "Vehicular"
    },
    {
        "accident_type": "Others"
    }
])

db.violation_types.insertMany([
    {
        "violation_type": "Electrical"
    },
    {
        "violation_type": "Fall protection"
    },
    {
        "violation_type": "Hazard communication"
    },
    {
        "accident-type": "Housekeeping"
    },
    {
        "violation_type": "Lock out/ Tag out"
    },
    {
        "violation_type": "Machine guarding"
    },
    {
        "violation_type": "Scaffolding"
    },
    {
        "violation_type": "Others"
    }
])



<div>
    <label>First Name</label>
    <input type="text" class="form-control" name="first_name">
    <!-- <input type="text" class="form-control {%if 'first_name_too_short' in errors or 'first_name_not_letter' in errors%} is-invalid {%endif%}" value="{{previous_values.first_name}}">
    {%if 'first_name_too_short' in errors or 'first_name_not_letter' in errors%}
    <div class="invalid-feedback">
          {{ errors.first_name_too_short or errors.first_name_not_letter}} 
    </div>
    {%endif%}   -->
</div>

<div>
    <label>Last Name</label>
    <input type="text" class="form-control" name="last_name">
    <!-- <input type="text" class="form-control {%if 'last_name_too_short' in errors or 'last_name_not_letter' in errors%} is-invalid {%endif%}" value="{{previous_values.last_name}}">
    {%if 'last_name_too_short' in errors or 'last_name_not_letter' in errors%}
    <div class="invalid-feedback">
          {{ errors.last_name_too_short or errors.last_name_not_letter}} 
    </div>
    {%endif%}   -->
</div>
<div>
    <label>Contact Number</label>
    <input type="text" class="form-control" name="contact_number">
    <!-- <input type="text" class="form-control {%if 'contact_number_must_be_8' in errors or 'contact_number_not_a_number' in errors%} is-invalid {%endif%}" value="{{previous_values.contact_number}}">
    {%if 'contact_number_must_be_8' in errors or 'contact_number_not_a_number' in errors%}
    <div class="invalid-feedback">
          {{ errors.contact_number_must_be_8 or errors.contact_number_not_a_number}} 
    </div>
    {%endif%}  -->
</div>
<div>
    <label>Email</label>
    <input type="text" class="form-control" name="email">
    <!-- <input type="text" class="form-control {%if 'proper_email' in errors %} is-invalid {%endif%}" value="{{previous_values.email}}">
    {%if 'proper_email' in errors%}
    <div class="invalid-feedback">
          {{ errors.proper_email}} 
    </div>
    {%endif%}  -->
</div>

    <input type="text" name="date" class="form-control {%if 'date_not_number' in errors or 'date_wrong_format' in errors%} is-invalid {%endif%}" value="{{previous_values.date}}">
    {%if 'date_not_number' in errors or 'date_wrong_format' in errors%}
    <div class="invalid-feedback">
          {{errors.date_not_number or errors.date_wrong_format}} 
    </div>
    {%endif%} 



            <!-- <div class="row" id="log">
                <a href="{{url_for('login')}}" class="btn btn-primary">Login</a>
                <a href="{{url_for('logout')}}" class="btn btn-secondary">Logout</a>

        </div>
        <h2>Safety Officers</h2>
        <div class="row" id="officers">
                <a href="{{url_for('show_officers')}}" class="btn btn-primary">View All</a>
                <a href="{{url_for('create_officers')}}" class="btn btn-secondary">Register</a>
        </div>
        <h2>Choose Report Type</h2>
        <div id="definition">
            <img src="static/image/definition.png">
        </div>
        <div class="row" id="reports">
            <div class="report" id="accident">
                <a href="{{url_for('show_accident_reports')}}" class="btn btn-primary">Read Accident Reports</a>
                <a href="{{url_for('show_create_accident_report')}}" class="btn btn-secondary">Create Accident Reports</a>
            </div>
            <div class="report" id="near-miss">
                <a href="{{url_for('show_near_miss_reports')}}" class="btn btn-primary">Read Near Miss Reports</a>
                <a href="{{url_for('show_create_near_miss_report')}}" class="btn btn-secondary">Create Near Miss Reports</a>
            </div>
            <div class="report" id="violation">
                <a href="{{url_for('show_violation_reports')}}" class="btn btn-primary">Read Violation Reports</a>
                <a href="{{url_for('show_create_violation_report')}}" class="btn btn-secondary">Create Violation Reports</a>
            </div>
    </div> -->