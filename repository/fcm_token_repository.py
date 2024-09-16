from datetime import datetime
from domain.entity.fcm_tokens import FCMToken
from domain import session_scope
import logging


class FCMTokenRepository:
    def __init__(self):
        pass

    def register_token(self, user_id, fcm_token, device_type):

        with session_scope() as session:
            try:
                # 1. Check if there is user given userId
                existing_token = session.query(FCMToken).filter_by(user_id=user_id, fcm_token=fcm_token).first()

                if existing_token:
                    existing_token.updated_at = datetime.now()
                    session.commit()
                    logging.info(f" A New token is registered for user {user_id}")
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
                    logging.info(f" A New token is registered for user {user_id}")

            except Exception as e:
                logging.error(f"Error registering FCM token for user {user_id}: {e}")
                session.rollback()

    def unregister_token(self, user_id, fcm_token):

        with session_scope() as session:
            try:
                existing_token = session.query(FCMToken).filter_by(user_id=user_id, fcm_token=fcm_token).first()

                if existing_token:
                    session.delete(existing_token)
                    session.commit()
                    logging.info(f" Unregistered the token for user {user_id}")
                    return True
                else:
                    logging.info(f" Invalid token for user {user_id}")
                    return False

            except Exception as e:
                logging.error(f"Error unregistering FCM token for user {user_id}: {e}")
                session.rollback()
                return False