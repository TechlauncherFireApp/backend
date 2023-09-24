from flask import Blueprint
from flask_restful import reqparse, Resource, fields, marshal_with, Api

from controllers.v2 import volunteer_availability_field
from domain import session_scope
from repository.volunteer_repository import *

from services.jwk import requires_auth

'''
Define Data Input
 {
     volunterrID: String
 }

'''

parser = reqparse.RequestParser()
parser.add_argument('volunteerID', action='store', type=str)

resource_fields = {
    'ID': fields.String,
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


# Handle the Recommendation endpoint
class Volunteer(Resource):
    @requires_auth
    @marshal_with(resource_fields)
    def get(self):
        args = parser.parse_args()
        if args["volunteerID"] is None:
            return {"success": False}

        with session_scope() as session:
            rtn = []
            for row in list_volunteers(session, args["volunteerID"]):
                # Access protected _asdict() to return the keyed tuple as a dict to enable flask_restful to marshal
                # it correctly. The alternative method is less tidy.
                rtn.append(row)
            return rtn[0]


volunteer_bp = Blueprint('volunteer', __name__)
api = Api(volunteer_bp)
api.add_resource(Volunteer, '/volunteer')