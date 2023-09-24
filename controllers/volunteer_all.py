from flask import Blueprint
from flask_restful import Resource, fields, marshal_with, Api

from controllers.v2 import volunteer_availability_field
from domain import session_scope
from repository.volunteer_repository import *
from services.jwk import requires_auth

'''
No Data Input
--
Define Data Output

{
    "results" : [{
        "id": String
        "firstName": String
        "lastName": String
        "email": String
        "mobileNo": String
        "prefHours": Integer
        "expYears": Integer
        "possibleRoles": [String]
        "qualifications": [String]
        "availabilities": [[DateTimeString iso8601, DateTimeString iso8601]]
    }]
}
'''

volunteer_list_field = {
    'ID': fields.String,
    'role': fields.Integer,
    'firstName': fields.String,
    'lastName': fields.String,
    'email': fields.String,
    'mobileNo': fields.String,
    'prefHours': fields.Integer,
    'expYears': fields.Integer,
    'qualifications': fields.List(fields.String),
    'availabilities': fields.Nested(volunteer_availability_field),
    'possibleRoles': fields.List(fields.String),
}

resource_fields = {
    'results': fields.List(fields.Nested(volunteer_list_field)),
}


# Handle the Recommendation endpoint
class VolunteerAll(Resource):

    @requires_auth
    @marshal_with(resource_fields)
    def get(self):
        with session_scope() as session:
            return {"success": True, "results": list_volunteers(session)}


volunteer_all_bp = Blueprint('volunteer_all', __name__)
api = Api(volunteer_all_bp)
api.add_resource(VolunteerAll, '/volunteer/all')
