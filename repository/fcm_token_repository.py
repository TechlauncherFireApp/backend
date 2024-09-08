from datetime import datetime
from domain.entity.fcm_tokens import FCMToken
from domain import session_scope, User
import logging


class FCMTokenRepository:
    def __init__(self):
        pass

    def check_user_exists(self, user_id):

        # Check if a user with the given user_id exists
        with session_scope() as session:
            user = session.query(User).filter_by(id=user_id).first()
            return user is not None

    def register_token(self, user_id, fcm_token, device_type):

        with session_scope() as session:
            try:
                # 1. Check if there is user given userId
                existing_token = session.query(FCMToken).filter_by(user_id=user_id, fcm_token=fcm_token).first()

                if existing_token:
                    existing_token.updated_at = datetime.now()
                    session.commit()
                    # logging.info(f" Token is already existed")
                else:
                    new_token = FCMToken(
                        user_id=user_id,
                        fcm_token=fcm_token,
                        device_type=device_type,
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    session.add(new_token)
                    session.commit()
                    # logging.info(f" A New token is registered for user {user_id}")

            except Exception as e:
                # logging.error(f"Error registering FCM token for user {user_id}: {e}")
                session.rollback()  # Roll back the transaction if an error occurs

    def unregister_token(self, fcm_token):
        pass