from flask import Blueprint
from flask_restful import reqparse, fields, Resource, marshal_with, Api

from domain import session_scope

from repository.diet_requirement_repository import get_dietary_requirements


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

    @marshal_with(result_fields)
    def get(self):
        """
        Returns:
            The dietary requirement data for the specified user
        """
        try:
            args = get_parser.parse_args()
            user_id = args['user_id']

            with session_scope() as session:
                diet_requirement = get_dietary_requirements(session, user_id)

            return {"diet_requirement": diet_requirement, "success": True}
        except Exception as e:
            print(f"Error: {e}")
            return {"success": False}, 400




diet_requirement_retrieval_bp = Blueprint('diet_requirement_retrieval', __name__)
api = Api(diet_requirement_retrieval_bp, '/dietary')
api.add_resource(RetrieveDietaryRequirement, '/getDietaryRequirement')
