import logging
from datetime import datetime
from domain.entity.fcm_tokens import FCMToken
from domain import session_scope
from exception import InvalidTokenError
from sqlalchemy.exc import SQLAlchemyError


class FCMTokenRepository:
    def __init__(self):
        pass

    def register_token(self, user_id: int, fcm_token: str, device_type: str) -> None:

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

    def unregister_token(self, user_id: int, fcm_token: str) -> bool:

        with session_scope() as session:
            try:
                existing_token = session.query(FCMToken).filter_by(user_id=user_id, fcm_token=fcm_token).first()

                if existing_token:
                    session.delete(existing_token)
                    session.commit()
                    logging.info(f" Unregistered the token for user {user_id}")
                    return True
                else:
                    logging.error(f"Invalid token for user {user_id}")
                    raise InvalidTokenError(f"Invalid token for user {user_id}")

            except SQLAlchemyError as e:
                logging.error(f"Database error while unregistering FCM token for user {user_id}:{e}")
                session.rollback()
                raise e
