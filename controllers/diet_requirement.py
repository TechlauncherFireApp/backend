from flask import Blueprint, request
from flask_restful import reqparse, fields, Resource, marshal_with, Api
from typing import List

from domain import session_scope
from domain.entity.diet_requirement import DietRequirement
from domain.type.dietary import DietaryRequirements, DietaryRestriction
from repository.diet_repository import save_dietary_requirements

# id_parser = reqparse.RequestParser()
# id_parser.add_argument('user_id', type=int, required=True)

# diet_parser = reqparse.RequestParser()
# diet_parser.add_argument('halal', type=bool, required=False)
# diet_parser.add_argument('vegetarian', type=bool, required=False)
# diet_parser.add_argument('vegan', type=bool, required=False)
# diet_parser.add_argument('nut_allergy', type=bool, required=False)
# diet_parser.add_argument('shellfish_allergy', type=bool, required=False)
# diet_parser.add_argument('gluten_intolerance', type=bool, required=False)
# diet_parser.add_argument('kosher', type=bool, required=False)
# diet_parser.add_argument('lactose_intolerance', type=bool, required=False)
# diet_parser.add_argument('diabetic', type=bool, required=False)
# diet_parser.add_argument('egg_allergy', type=bool, required=False)
# diet_parser.add_argument('other', type=str, required=True)

new_parser = reqparse.RequestParser()
# new_parser.add_argument('dietary_requirements', type=DietaryRequirements)
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
        print(diet_args)
        # dic_diet = from_dietary_requirements(diet_args)

        with session_scope() as session:
            return {'result': save_dietary_requirements(session, user_id, diet_args)}


diet_requirement_bp = Blueprint('diet_requirement', __name__)
api = Api(diet_requirement_bp, '/dietary')
api.add_resource(GetDietaryRequirement, '/getDietaryRequirement')
