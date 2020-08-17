// To test queries before inserting to mongo


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
    "_id":ObjectId("5f3a25ab2cde7c1882d3e0ad")
}, {
    "$pull": {
        "reports": {
              "_id":ObjectId("5f3a34582cde7c1882d3e0b4")
        }
    }
})