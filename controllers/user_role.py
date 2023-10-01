from flask import Blueprint
from flask_restful import fields, Resource, marshal_with, Api, reqparse

from domain import session_scope, UserType
from repository.user_role_repository import get_user_roles, add_user_role, delete_user_role

from services.jwk import requires_auth, has_role

get_fields = {
    'userId': fields.Integer,
    'roleId': fields.Integer,
}

post_fields = {
    'userRoleId': fields.Integer
}

patch_fields = {
    'success': fields.Boolean
}

parser = reqparse.RequestParser()
parser.add_argument('userId', action='store', type=str)
parser.add_argument('roleId', action='store', type=str)


class UserRole(Resource):
    @requires_auth
    @has_role(UserType.ROOT_ADMIN)
    @marshal_with(get_fields)
    def get(self):
        with session_scope() as session:
            return get_user_roles(session)

    @requires_auth
    @has_role(UserType.ROOT_ADMIN)
    @marshal_with(post_fields)
    def post(self):
        args = parser.parse_args()
        if args['userId'] is None or args['roleId'] is None:
            return
        with session_scope() as session:
            role_id = add_user_role(session, args['userId'], args['roleId'])
            return {'id': role_id}

    @has_role(UserType.ROOT_ADMIN)
    @marshal_with(patch_fields)
    def patch(self):
        args = parser.parse_args()
        if args['userId'] is None or args['roleId'] is None:
            return
        with session_scope() as session:
            return delete_user_role(session, args['userId'], args['roleId'])


user_role_bp = Blueprint('user-role', __name__)
api = Api(user_role_bp)
api.add_resource(UserRole, '/user-role')
