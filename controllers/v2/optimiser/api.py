import logging
from flask_restful import Resource, marshal_with, reqparse
from repository.fcm_token_repository import FCMTokenRepository
from .response_models import optimiser_response_model
from repository.shift_repository import ShiftRepository
from services.jwk import requires_auth, is_user_or_has_role
from domain import UserType, session_scope
from controllers.v2.v2_blueprint import v2_api
from services.optimiser.optimiser import Optimiser


# Initialise parser for potential arguments in future extensions (if needed)
parser = reqparse.RequestParser()
parser.add_argument('debug', type=bool, required=False, help="Optional debug mode flag.")


class OptimiserResource(Resource):

    optimiser_repository: ShiftRepository
    fcm_token_repository: FCMTokenRepository

    def __init__(
            self,
            optimiser_repository: ShiftRepository = ShiftRepository(),
            fcm_token_repository: FCMTokenRepository = FCMTokenRepository()
    ):
        self.optimiser_repository = optimiser_repository
        self.fcm_token_repository = fcm_token_repository

    @requires_auth
    @is_user_or_has_role(None, UserType.ROOT_ADMIN)
    @marshal_with(optimiser_response_model)  # Use the marshalling model
    def post(self):
        # Parse debug argument
        try:
            args = parser.parse_args()
        except Exception:
            args = {}
        # Default debug to False if it's not provided or the body is empty
        debug = args.get('debug', False)

        try:
            with session_scope() as session:
                # Initialise and run the optimiser
                optimiser = Optimiser(
                    session=session,
                    repository=self.optimiser_repository,
                    debug=debug,
                    fcm_token_repository=self.fcm_token_repository
                )

                result = optimiser.solve()
                optimiser.save_result(result)

                # Return raw data, the marshaller will format it
                return {
                    "message": "Optimisation completed successfully",
                    "result": str(result)
                }

        except Exception as e:
            logging.error(f"Error running optimiser: {e}")
            return {"message": "Internal server error", "result": str(e)}, 500


# Register the OptimiserResource in the blueprint
v2_api.add_resource(OptimiserResource, '/v2/optimiser')
