import logging
import os
import firebase_admin
from firebase_admin import credentials, messaging, exceptions
from typing import List, Optional


class NotificationService:

    def __init__(self):

        if not firebase_admin._apps:
            cred_path = f"{os.getcwd()}/google-credentials.json"
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)

    def send_notification(self, fcm_token_list: List[str], title: str, body: str, data: Optional[dict] = None) -> None:
        """
        Send message to the user device given a list of FCM tokens.

        :param fcm_token_list: List of FCM tokens to send the notification to.
        :param title: The title of the notification.
        :param body: The body content of the notification.
        :param data: Optional additional data for the notification.
        """
        if not fcm_token_list:
            logging.warning("No FCM tokens provided. Cannot send notification.")

        for token in fcm_token_list:

            message = messaging.Message(
                notification=messaging.Notification(title=title, body=body),
                data=data or {},
                token=token
            )

            try:
                response = messaging.send(message)
                logging.info(f"Successfully sent message to token: {token}")
            except exceptions.FirebaseError as e:
                logging.error(f"Firebase error for token {token}: {e}")
            except Exception as e:
                logging.error(f"Error sending message to token {token}: {e}")
