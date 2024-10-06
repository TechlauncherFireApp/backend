import logging
from typing import List, Optional
from datetime import datetime
from domain.entity.fcm_tokens import FCMToken
from domain import session_scope
from exception import InvalidTokenError
from sqlalchemy.exc import SQLAlchemyError
from services.notification_service import NotificationService


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

    def unregister_token(self, user_id: int, fcm_token: str) -> None:

        with session_scope() as session:
            try:
                existing_token = session.query(FCMToken).filter_by(user_id=user_id, fcm_token=fcm_token).first()

                if existing_token:
                    session.delete(existing_token)
                    session.commit()
                    logging.info(f" Unregistered the token for user {user_id}")
                else:
                    logging.error(f"Invalid token for user {user_id}")
                    raise InvalidTokenError(f"Invalid token for user {user_id}")

            except SQLAlchemyError as e:
                logging.error(f"Database error while unregistering FCM token for user {user_id}:{e}")
                session.rollback()
                raise e

    def get_fcm_token(self, user_id: int) -> List[str]:
        """
        Get FCM tokens for a user

        :param user_id: The user id
        :return: A list of FCM tokens for a given user.
        """
        with session_scope() as session:
            try:
                # Query to get all tokens for the given user_id
                existing_tokens = session.query(FCMToken).filter_by(user_id=user_id).all()

                if not existing_tokens:
                    logging.info(f"No active FCM token found for user {user_id}")
                    return []

                fcm_token_list = [token.fcm_token for token in existing_tokens]
                return fcm_token_list

            except SQLAlchemyError as e:
                logging.error(f"Database error while retrieving FCM token for user {user_id}: {e}")

                raise e

    def notify_user(
            self,
            user_id: Optional[int] = None,
            fcm_token_list: Optional[List[str]] = None,
            title: Optional[str] = None,
            body: Optional[str] = None,
            data: Optional[dict] = None
    ) -> None:
        """
        Notify a user by sending a notification to their device.

        This function either accepts a user id to look up tokens or take a list of FCM tokens.

        :param user_id: The user id (optional if fcm token list is provided)
        :param fcm_token_list: A list of FCM tokens (optional if user id is provided)
        :param title: The title of the notification (required)
        :param body: The body of the notification (required)
        :param data: The data of the notification (optional)
        """

        # Ensure either user_id or fcm_token_list is provided
        if user_id is None and fcm_token_list is None:
            raise ValueError("Either user_id or fcm_token_list must be provided")

        if title is None or body is None:
            raise ValueError("Title and body must be provided")

        # Get the token list if user_id is provided, otherwise use fcm_token_list
        if user_id is not None:
            token_list = self.get_fcm_token(user_id)
        else:
            token_list = fcm_token_list

        # Ensure token_list is not empty
        if not token_list:
            raise ValueError("No valid FCM tokens found or provided")

        # Call notification service function
        notification_service = NotificationService()
        notification_service.send_notification(
            token_list, title, body, data
        )
