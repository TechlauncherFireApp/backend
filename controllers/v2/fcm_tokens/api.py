import logging
from repository.fcm_token_repository import FCMTokenRepository
from flask_restful import Resource, reqparse
from controllers.v2.v2_blueprint import v2_api

parser = reqparse.RequestParser()
parser.add_argument('token', type=str, required=True, help ="Token must be provided.")
parser.add_argument('device_type', type=str, required=True, help ="DeviceType must be provided.")

class FCMToken(Resource):

    token_repository: FCMTokenRepository

    def __init__(self, token_repository: FCMTokenRepository = FCMTokenRepository()):
        self.token_repository = token_repository

    def post(self, user_id):

        args = parser.parse_args()
        fcm_token = args['token']
        device_type = args['device_type']

        try:
            # 1. Check if the user exist
            if not self.token_repository.check_user_exists(user_id):
                return {"message": "User not found"}, 400

            # 2. Register the token for the user
            self.token_repository.register_token(user_id, fcm_token, device_type)
            return {"message": "FCM token registered successfully"}, 200

        except Exception as e:

            logging.error(f"Error registering FCM token: {e}")
            return {"message": "Internal server error"}, 500


v2_api.add_resource(FCMToken,'/v2/user/<int:user_id>/token')


unregister_parser = reqparse.RequestParser()
unregister_parser.add_argument('userId', type=int, required=True, help ="userId must be provided.")
unregister_parser.add_argument('token', type=str, required=True, help ="Token must be provided.")


class FCMTokenUnregister(Resource):

    token_repository: FCMTokenRepository

    def __init__(self, token_repository: FCMTokenRepository = FCMTokenRepository()):
        self.token_repository = token_repository

    def post(self):
        args = unregister_parser.parse_args()
        user_id = args['userId']
        fcm_token = args['token']

        try:
            if not self.token_repository.check_user_exists(user_id):
                return {"message": "User not found"}, 400

            if self.token_repository.unregister_token(user_id, fcm_token):
                return {"message": "FCM token unregistered successfully"}, 200
            else:
                return {"message": "FCM token unregistration failed"}, 400

        except Exception as e:
            logging.error(f"Error unregistering FCM token: {e}")
            return {"message": "Internal server error"}, 500


v2_api.add_resource(FCMTokenUnregister, '/v2/unregister-token')
