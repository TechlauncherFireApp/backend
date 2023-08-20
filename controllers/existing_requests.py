from flask import Blueprint
from flask_restful import reqparse, Resource, fields, marshal_with, Api

from domain import session_scope
from repository.request_repository import *

from services.jwk import requires_auth

'''
Define Data Input

PATCH
{
    "requestId": Int
    "status": String
}

DELETE
{
    "requestId": String
}
'''

parser = reqparse.RequestParser()
parser.add_argument('requestId', action='store', type=int)
parser.add_argument('status', action='store', type=str)

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('requestId', action='store', type=str)

'''
Define Data Output

GET
{
    "id": String,
    "title": String
}

PATCH
{
    "success": Boolean
}

DELETE
{
    "success": Boolean
}
'''

get_resource_obj = {
    "id": fields.String,
    "title": fields.String,
    "status": fields.String
}

get_resource_list = {
    "success": fields.Boolean,
    "results": fields.List(fields.Nested(get_resource_obj))
}


# Handle the Recommendation endpoint
class ExistingRequests(Resource):
    @requires_auth
    @marshal_with(get_resource_list)
    def get(self):
        with session_scope() as session:
            res = get_existing_requests(session)
            return {"success": True, "results": res}

    @marshal_with(get_resource_list)
    def patch(self):
        args = parser.parse_args()
        with session_scope() as session:
            result = update_request_status(session, args["requestId"], args["status"])
            return {"success": result}

    @marshal_with(get_resource_list)
    def delete(self):
        args = delete_parser.parse_args()
        with session_scope() as session:
            result = delete_request(session, args["requestId"])
            return {"success": result}


existing_requests_bp = Blueprint('existing_requests', __name__)
api = Api(existing_requests_bp)
api.add_resource(ExistingRequests, '/existing_requests')
