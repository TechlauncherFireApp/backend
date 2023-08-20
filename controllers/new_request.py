from flask import Blueprint
from flask_restful import reqparse, Resource, fields, marshal_with, Api

from domain import session_scope
from repository.request_repository import *

from services.jwk import requires_auth

'''
Define Data Input

POST
{
    "title": String
    "status": String
}

DELETE
{
    "requestID": String
}
'''

parser = reqparse.RequestParser()
parser.add_argument('title', action='store', type=str)
parser.add_argument('status', action='store', type=str)

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('requestID', action='store', type=str)

'''
Define Data Output

POST
{
    "id": String
}

DELETE
{
    "success": Boolean
}
'''

resource_fields = {
    "id": fields.String
}


# Make a New Request inside the DataBase
class NewRequest(Resource):
    @requires_auth
    @marshal_with(resource_fields)
    def post(self):
        args = parser.parse_args()
        if args["title"] is None:
            return
        with session_scope() as session:
            new_id = new_request(session, args["title"], args["status"])
            return {"id": new_id}

    # Delete a Request inside the DataBase
    @marshal_with(resource_fields)
    def delete(self):
        args = delete_parser.parse_args()
        with session_scope() as session:
            result = delete_request(session, args["requestID"])
            return result


new_request_bp = Blueprint('new_requests', __name__)
api = Api(new_request_bp)
api.add_resource(NewRequest, "/new_request")
