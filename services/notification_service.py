import logging
import os
import firebase_admin
from firebase_admin import credentials, messaging, exceptions


class NotificationService:


    def __init__(self):

        if not firebase_admin._apps:
            cred_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', r"C:\Users\User\backend\google-credentials.json")
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)

    def send_notification(self, fcm_token, title, body, data=None):
        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            data=data or {},
            token=fcm_token
        )

        try:
            response = messaging.send(message)
            logging.info("Successfully sent message: {}".format(response))
            return response
        except exceptions.FirebaseError as e:
            logging.error("Firebase error: {}".format(e))
            raise e
        except Exception as e:
            logging.error("Error sending message: {}".format(e))
            raise e



"""
This file is temporarily used for testing purpose.
"""
if __name__ == '__main__':


    import logging
    from services.notification_service import NotificationService


    logging.basicConfig(level=logging.INFO)
    notification_service = NotificationService()
    fcm_token = 'cE2oUPG1Q-6guB8o52K7Ag:APA91bGJXqQScQbUk7vVpItG64vZ4nnzY3ClpjJA-SC5e02i23Cx__9h08lOOdKS9r6Nq6ZMC0YPOJ7sKI_D3wHELUjJdQL1XYGmj3bTQgFR-NIXKDN9PQEbdUi60HGURFrru-BORUgR'
    title = 'Test'
    body = 'This is a test notification.'
    data_payload = {'Test': 'value1', 'key2': 'value2'}

    notification_service.send_notification(
        fcm_token=fcm_token,
        title=title,
        body=body,
        data=data_payload
    )
