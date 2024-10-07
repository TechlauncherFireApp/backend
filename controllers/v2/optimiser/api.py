from flask_restful import Resource, marshal_with, reqparse
from .response_models import optimiser_response_model
from repository.shift_repository import ShiftRepository
from repository.fcm_token_repository import FCMTokenRepository
from services.jwk import requires_auth, is_user_or_has_role
from domain import UserType, session_scope
from controllers.v2.v2_blueprint import v2_api
from services.optimiser.optimiser import Optimiser
import logging

# Initialise parser for potential arguments in future extensions (if needed)
parser = reqparse.RequestParser()
parser.add_argument('debug', type=bool, required=False, help="Optional debug mode flag.")


class OptimiserResource(Resource):
    optimiser_repository: ShiftRepository

    def __init__(self, optimiser_repository: ShiftRepository = ShiftRepository()):
        self.optimiser_repository = optimiser_repository

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
                optimiser = Optimiser(session=session, repository=self.optimiser_repository, debug=debug)
                result = optimiser.solve()
                optimiser.save_result(result)

                # Extract user id from result
                user_id_list = optimiser.extract_user_ids_from_result(result)

                # check if there is no user
                if not user_id_list:
                    logging.info("No users found to notify.")
                else:
                    # Initialize FCM token repository for retrieving token and notifying user
                    fcm_token_repo = FCMTokenRepository()

                    # Loop through user id, retrieve token and send message
                    for user_id in user_id_list:
                        title = "New Shift Assignment"
                        body = "You have been assigned to a new shift."
                        try:
                            fcm_token_repo.notify_user(user_id=user_id, title=title, body=body)
                        except Exception as e:
                            logging.error(f"Error sending notification to user {user_id}: {e}")

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
