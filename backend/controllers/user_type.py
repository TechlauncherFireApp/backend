from flask import Blueprint
from flask_restful import fields, Resource, marshal_with, Api, reqparse

from domain import session_scope
from repository.user_repository import demote_user, promote_user, self_demote

patch_fields = {
    'success': fields.Boolean
}

parser = reqparse.RequestParser()
parser.add_argument('userId', action='store', type=str)
parser.add_argument('typeChange', action='store', type=str)


class UserType(Resource):

    @marshal_with(patch_fields)
    def patch(self):
        args = parser.parse_args()
        result = False
        if args['userId'] is None or args['typeChange'] not in ('promote', 'demote', 'self-demote'):
            return {'success': result}
        # print('patch', args['userId'], args['typeChange'])
        with session_scope() as session:
            if args['typeChange'] == 'promote':
                result = promote_user(session, args['userId'])
            if args['typeChange'] == 'demote':
                result = demote_user(session, args['userId'])
            if args['typeChange'] == 'self-demote':
                result = self_demote(session, args['userId'])
        return {'success': result}


user_type_bp = Blueprint('user-type', __name__)
api = Api(user_type_bp)
api.add_resource(UserType, '/user-type')
