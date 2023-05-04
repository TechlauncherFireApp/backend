from flask_restful import Resource, marshal_with, reqparse

from controllers.v2.v2_blueprint import v2_api
from domain import session_scope, UserType
from controllers.v2.reference.response_models import role_model, id_model
from repository.reference_repository import get_roles, add_role, toggle_role, \
    delete_role
from services.jwk import requires_auth, has_role

role_parser = reqparse.RequestParser()
role_parser.add_argument('id', action='store', type=str)
role_parser.add_argument('name', action='store', type=str)
role_parser.add_argument('code', action='store', type=str)

class RoleReference(Resource):
    @requires_auth
    @marshal_with(role_model)
    def get(self):
        with session_scope() as session:
            return get_roles(session)

    @has_role(UserType.ROOT_ADMIN)
    @marshal_with(id_model)
    def post(self):
        args = role_parser.parse_args()
        print("name:", args['name'], "code:", args['code'])
        if args['name'] is None or args['name'] == '' or args['code'] is None or args['code'] == '':
            print('empty return')
            return
        with session_scope() as session:
            role_id = add_role(session, args['name'], args['code'])
            return {'id': role_id}

    @has_role(UserType.ROOT_ADMIN)
    def patch(self):
        args = role_parser.parse_args()
        if args['id'] is None or args['id'] == '':
            return
        with session_scope() as session:
            toggle_role(session, args['id'])
        return

    @has_role(UserType.ROOT_ADMIN)
    def delete(self):
        args = role_parser.parse_args()
        if args['id'] is None or args['id'] == '':
            return
        with session_scope() as session:
            delete_role(session, args['id'])
        return


v2_api.add_resource(RoleReference, '/v2/reference/roles')
