from flask_restful import fields

from controllers.v2.diet import volunteer_dietary_requirement

volunteer_availability_field = {
    "Monday": fields.List(fields.List(fields.Float)),
    "Tuesday": fields.List(fields.List(fields.Float)),
    "Wednesday": fields.List(fields.List(fields.Float)),
    "Thursday": fields.List(fields.List(fields.Float)),
    "Friday": fields.List(fields.List(fields.Float)),
    "Saturday": fields.List(fields.List(fields.Float)),
    "Sunday": fields.List(fields.List(fields.Float)),
}

volunteer_listing_model = {
    'ID': fields.String,
    'firstName': fields.String,
    'lastName': fields.String,
    'qualification': fields.List(fields.String),
}


volunteer_personal_info = {
    'ID': fields.String,
    'firstName': fields.String,
    'lastName': fields.String,
    'email': fields.String,
    'mobileNo': fields.String,
    'prefHours': fields.Integer,
    'expHours': fields.Integer,
    'qualification': fields.List(fields.String),
    'possibleRoles': fields.List(fields.String),
    'availabilities': fields.Nested(volunteer_availability_field),
    'dietaryRequirements': fields.Nested(volunteer_dietary_requirement)
}