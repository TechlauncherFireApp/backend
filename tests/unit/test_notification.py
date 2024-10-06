import unittest
import os
from unittest.mock import patch
from repository.fcm_token_repository import FCMTokenRepository
from services.notification_service import NotificationService


class TestNotificationService(unittest.TestCase):


    @patch('firebase_admin.initialize_app')
    @patch('firebase_admin.credentials.Certificate')
    def test_credentials_loading(self, mock_certificate, mock_initialize_app):

        # Mock the Certificate and initialize_app calls
        mock_certificate.return_value = "mocked_credential"

        # Calculate the expected path dynamically
        expected_cred_path = f"{os.getcwd()}/google-credentials.json"

        # Instantiate the NotificationService, which should trigger credentials loading
        notification_service = NotificationService()

        # Assert the credentials were loaded correctly with the dynamic path
        mock_certificate.assert_called_once_with(expected_cred_path)
        mock_initialize_app.assert_called_once_with("mocked_credential")

    @patch('firebase_admin.initialize_app')
    @patch('firebase_admin.credentials.Certificate')
    @patch('firebase_admin.messaging.send')
    @patch.object(FCMTokenRepository, 'get_fcm_token')
    def test_notify_user_with_user_id(self, mock_get_fcm_token, mock_send, mock_certificate, mock_initialize_app):
        # Mock the get_fcm_token method to return a list of FCM tokens
        mock_get_fcm_token.return_value = ['mock_token_1', 'mock_token_2']

        # Mock the NotificationService's send_notification method
        mock_send.return_value = "mock_response"

        # Mock the certificate loading to avoid FileNotFoundError
        mock_certificate.return_value = "mocked_credential"
        mock_initialize_app.return_value = None

        # Instantiate the repository and call notify_user with a user_id
        fcm_token_repo = FCMTokenRepository()
        fcm_token_repo.notify_user(user_id=6, fcm_token_list=None, title="Test Title", body="Test Body")

        # Check that get_fcm_token was called with the correct user_id
        mock_get_fcm_token.assert_called_once_with(6)

        # Define a helper function to check attributes of the messaging.Message
        def message_matcher(expected_title, expected_body, expected_token):
            def match(message):
                return (message.notification.title == expected_title and
                        message.notification.body == expected_body and
                        message.token == expected_token)
            return match

        # Check that messaging.send was called for each token
        self.assertTrue(any(message_matcher("Test Title", "Test Body", "mock_token_1")(call[0][0])
                            for call in mock_send.call_args_list))
        self.assertTrue(any(message_matcher("Test Title", "Test Body", "mock_token_2")(call[0][0])
                            for call in mock_send.call_args_list))

        # Ensure that messaging.send was called twice (once for each token)
        self.assertEqual(mock_send.call_count, 2)


if __name__ == '__main__':
    unittest.main()
