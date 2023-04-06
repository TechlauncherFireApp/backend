from flask import Blueprint, request
from flask_restful import reqparse, fields, Resource, marshal_with, Api

from domain import session_scope
from domain.type.dietary import DietaryRestriction
from repository.change_diet_repository import update_dietary_requirements, get_user_by_id




# get frontend data
new_parser = reqparse.RequestParser()
new_parser.add_argument('user_id', type=int, required=True)
new_parser.add_argument('restrictions', type=DietaryRestriction, action='append')
new_parser.add_argument('custom_restrictions', type=str)


result_fields = {
    "result": fields.Boolean
}


class UpdateDietaryRequirement(Resource):
    """
    This is a class used to update dietary demand data in the database (if the user exists)
    """

    @marshal_with(result_fields)
    def post(self):
        """
        return:
               If the data update is successful, return True; Otherwise, return False
        """
        try:
            request.get_json(force=True)
            args = new_parser.parse_args()
            user_id = args['user_id']

            with session_scope() as session:
                # check whether user_id is exist
                if get_user_by_id(session, user_id):
                    # If exist, update dietary requirement
                    return {'result': update_dietary_requirements(session, user_id, args)}
                else:
                    # if not exist, return false
                    return {'result': False}
        except Exception as e:
            return {'result': False}, 400


diet_requirement_change_bp = Blueprint('change_diet_requirement', __name__)
api = Api(diet_requirement_change_bp, '/dietary')
api.add_resource(UpdateDietaryRequirement, '/changeDietaryRequirement')
