from flask import Blueprint, request
from flask_restful import reqparse, fields, Resource, marshal_with, Api

from domain import session_scope
from domain.type.dietary import DietaryRestriction
from repository.diet_repository import save_dietary_requirements

from repository.diet_requirement_repository import get_dietary_requirements, get_formatted_dietary_requirements
from repository.diet_requirement_repository import diet_requirement_to_dict
from services.jwk import requires_auth, JWKService

# getting the data from the frontend
new_parser = reqparse.RequestParser()
new_parser.add_argument('user_id', type=int)
new_parser.add_argument('restrictions', type=DietaryRestriction, action='append')
new_parser.add_argument('custom_restrictions', type=str)

options = [
    'halal',
    'vegetarian',
    'vegan',
    'nut_allergy',
    'shellfish_allergy',
    'gluten_intolerance',
    'kosher',
    'lactose_intolerance',
    'diabetic',
    'egg_allergy'
]


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


class DietaryOptions(Resource):

    def get(self):
        return [{
            "key": k,
            "display_name": k.replace('_', ' ').title()
        } for k in options], 200


class DietaryRequirement(Resource):
    """
        This is a class to store the data of dietary requirement to the database
        """

    @requires_auth
    def post(self):
        """
        Returns:
            True if the data is updated; False if the data is unable to upload
        """
        try:
            request.get_json(force=True)
            args = new_parser.parse_args()
            user_id = JWKService.decode_user_id()

            with session_scope() as session:
                save_dietary_requirements(session, user_id, args)
                return {'result': True}, 200
        except Exception as e:
            return {'result': False}, 400

    """
    This is a class to retrieve the dietary requirement data from the database
    """
    @requires_auth
    def get(self):
        try:
            user_id = JWKService.decode_user_id()
            if user_id is None:
                raise ValueError("user_id is required")
            elif user_id == -1:
                raise Exception("An error occurred while decoding the auth token.")

            with session_scope() as session:
                return get_formatted_dietary_requirements(session, user_id), 200


        except Exception as e:
            return {"custom_restrictions": "", "restrictions": []}, 400


diet_requirement_retrieval_bp = Blueprint('diet_requirement_retrieval', __name__)
api = Api(diet_requirement_retrieval_bp, '/dietary')
api.add_resource(DietaryRequirement, '/requirements')
api.add_resource(DietaryOptions, '/options')
