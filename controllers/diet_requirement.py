from flask import Blueprint, request
from flask_restful import reqparse, fields, Resource, marshal_with, Api

from domain import session_scope
from domain.type.dietary import DietaryRestriction
from repository.diet_repository import save_dietary_requirements

new_parser = reqparse.RequestParser()
new_parser.add_argument('user_id', type=int, required=True)
new_parser.add_argument('restrictions', type=DietaryRestriction, action='append')
new_parser.add_argument('custom_restrictions', type=str)

result_fields = {
    "result": fields.Boolean
}


class GetDietaryRequirement(Resource):
    @marshal_with(result_fields)
    def post(self):
        request.get_json(force=True)
        args = new_parser.parse_args()
        user_id = args['user_id']

        diet_args = new_parser.parse_args()

        with session_scope() as session:
            return {'result': save_dietary_requirements(session, user_id, diet_args)}


diet_requirement_bp = Blueprint('diet_requirement', __name__)
api = Api(diet_requirement_bp, '/dietary')
api.add_resource(GetDietaryRequirement, '/getDietaryRequirement')
