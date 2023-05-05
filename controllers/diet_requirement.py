from flask import Blueprint, request
from flask_restful import reqparse, fields, Resource, marshal_with, Api

from domain import session_scope
from domain.type.dietary import DietaryRestriction
from repository.diet_repository import save_dietary_requirements

from repository.diet_requirement_repository import get_dietary_requirements
from repository.diet_requirement_repository import diet_requirement_to_dict

# getting the data from the frontend
new_parser = reqparse.RequestParser()
new_parser.add_argument('user_id', type=int, required=True)
new_parser.add_argument('restrictions', type=DietaryRestriction, action='append')
new_parser.add_argument('custom_restrictions', type=str)

# the result for whether updating the data success
result_fields = {
    "result": fields.Boolean
}


class StoreDietaryRequirement(Resource):
    """
    This is a class to store the data of dietary requirement to the database
    """
    @marshal_with(result_fields)
    def post(self):
        """
        Returns:
            True if the data is updated; False if the data is unable to upload
        """
        try:
            request.get_json(force=True)
            args = new_parser.parse_args()
            user_id = args['user_id']

            with session_scope() as session:
                return {'result': save_dietary_requirements(session, user_id, args)}
        except Exception as e:
            return {'result': False}, 400


diet_requirement_bp = Blueprint('diet_requirement', __name__)
api = Api(diet_requirement_bp, '/dietary')
api.add_resource(StoreDietaryRequirement, '/storeDietaryRequirement')


##get the diet requirement from database
get_parser = reqparse.RequestParser()
get_parser.add_argument('user_id', type=int, required=True)

diet_requirement_fields = {
    'diet_id': fields.Integer,
    'user_id': fields.Integer,
    'halal': fields.Boolean,
    'vegetarian': fields.Boolean,
    'vegan': fields.Boolean,
    'nut_allergy': fields.Boolean,
    'shellfish_allergy': fields.Boolean,
    'gluten_intolerance': fields.Boolean,
    'kosher': fields.Boolean,
    'lactose_intolerance': fields.Boolean,
    'diabetic': fields.Boolean,
    'egg_allergy': fields.Boolean,
    'other': fields.String
}

result_fields = {
    "diet_requirement": fields.Nested(diet_requirement_fields),
    "success": fields.Boolean
}

class RetrieveDietaryRequirement(Resource):
    """
    This is a class to retrieve the dietary requirement data from the database
    """

    def get(self):
        try:
            user_id = request.args.get('user_id', None, type=int)
            if user_id is None:
                raise ValueError("user_id is required")

            with session_scope() as session:
                diet_requirement = get_dietary_requirements(session, user_id)
                diet_requirement_dict = diet_requirement_to_dict(diet_requirement)

            restrictions = []
            for key, value in diet_requirement_dict.items():
                if key not in ['diet_id', 'user_id', 'other'] and value:
                    display_name = key.replace('_', ' ').title()
                    restrictions.append({"key": key, "display_name": display_name})

            return {
                "custom_restrictions": diet_requirement_dict.get('other', ''),
                "restrictions": restrictions
            }, 200
        except Exception as e:
            return {"custom_restrictions": "", "restrictions": []}, 400

diet_requirement_retrieval_bp = Blueprint('diet_requirement_retrieval', __name__)
api = Api(diet_requirement_retrieval_bp, '/dietary')
api.add_resource(RetrieveDietaryRequirement, '/requirements')