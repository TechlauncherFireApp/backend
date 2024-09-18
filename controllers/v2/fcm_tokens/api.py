import logging
from repository.fcm_token_repository import FCMTokenRepository
from flask_restful import Resource, reqparse, marshal_with
from controllers.v2.v2_blueprint import v2_api
from services.jwk import requires_auth, JWKService
from controllers.v2.fcm_tokens.response_models import response_model
from repository.user_repository import UserRepository
from exception import InvalidTokenError
from sqlalchemy.exc import SQLAlchemyError


parser = reqparse.RequestParser()
parser.add_argument('token', type=str, required=True, help ="Token must be provided.")
parser.add_argument('device_type', type=str, required=True, help ="DeviceType must be provided.")
unregister_parser = reqparse.RequestParser()
unregister_parser.add_argument('token', type=str, required=True, help ="Token must be provided.")


class FCMToken(Resource):

    token_repository: FCMTokenRepository
    user_repository: UserRepository

    def __init__(
            self,
            token_repository: FCMTokenRepository = FCMTokenRepository(),
            user_repository: UserRepository = UserRepository()
    ):
        self.token_repository = token_repository
        self.user_repository = user_repository

    @requires_auth
    @marshal_with(response_model)
    def post(self, user_id: int):

        # Decode authenticated user id
        authenticated_user_id = JWKService.decode_user_id()

        # Check if they are matched
        if authenticated_user_id != user_id:
            return {"message": "User ID mismatch"}, 403

        # Check if decoding fail
        args = parser.parse_args()
        fcm_token = args['token']
        device_type = args['device_type']

        try:
            # 1. Check if the user exist
            if not self.user_repository.check_user_exists(user_id):
                return {"message": "User not found"}, 400

            # 2. Register the token for the user
            self.token_repository.register_token(user_id, fcm_token, device_type)
            return {"message": "FCM token registered successfully"}, 200

        except Exception as e:

            logging.error(f"Error registering FCM token: {e}")
            return {"message": "Internal server error"}, 500

    @requires_auth
    @marshal_with(response_model)
    def delete(self, user_id: int):

        # Decode authenticated user id
        authenticated_user_id = JWKService.decode_user_id()

        # Check if they are matched
        if authenticated_user_id != user_id:
            return {"message": "User ID mismatch"}, 403

        args = unregister_parser.parse_args()
        fcm_token = args['token']

        try:
            # Check if user exist
            if not self.user_repository.check_user_exists(user_id):
                return {"message": "User not found"}, 400

            # Unregister the token
            self.token_repository.unregister_token(user_id, fcm_token)
            return {"message": "FCM token unregistered successfully"}, 200

        except InvalidTokenError as e:
            logging.error(f"Error unregistering FCM token: {e}")
            return {"message": str(e)}, 400

        except Exception as e:
            logging.error(f"Error unregistering FCM token: {e}")
            return {"message": "Internal server error"}, 500


v2_api.add_resource(FCMToken,'/v2/user/<int:user_id>/token')
