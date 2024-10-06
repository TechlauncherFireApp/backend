import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock
from repository.fcm_token_repository import FCMTokenRepository
from domain.entity.fcm_tokens import FCMToken


class TestFCMTokenRepository(unittest.TestCase):

    @patch('repository.fcm_token_repository.session_scope')
    def test_get_fcm_token_success(self, mock_session_scope):
        # Set up the mock session and query
        mock_session = MagicMock()
        mock_query = mock_session.query.return_value
        mock_session_scope.return_value.__enter__.return_value = mock_session

        # Create a mock FCMToken object
        mock_fcm_token = FCMToken(
            user_id=6,
            fcm_token="mock_token_1",
            device_type="android",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_active=True
        )

        # Simulate tokens found in the database
        mock_query.filter_by.return_value.all.return_value = [mock_fcm_token]

        # Instantiate the repository and call the method
        fcm_token_repo = FCMTokenRepository()
        token_list = fcm_token_repo.get_fcm_token(6)

        # Assertions
        mock_query.filter_by.assert_called_once_with(user_id=6)
        self.assertEqual(token_list, ["mock_token_1"])

    @patch('repository.fcm_token_repository.session_scope')
    def test_get_fcm_token_no_tokens(self, mock_session_scope):
        # Set up the mock session and query
        mock_session = MagicMock()  # Mock session
        mock_query = mock_session.query.return_value
        mock_session_scope.return_value.__enter__.return_value = mock_session

        # Simulate no tokens found in the database
        mock_query.filter_by.return_value.all.return_value = []

        # Instantiate the repository and call the method
        fcm_token_repo = FCMTokenRepository()
        token_list = fcm_token_repo.get_fcm_token(6)

        # Assertions
        mock_query.filter_by.assert_called_once_with(user_id=6)  # Ensure correct query
        self.assertEqual(token_list, [])

    @patch('firebase_admin.credentials.Certificate')
    @patch('firebase_admin.initialize_app')
    @patch('repository.fcm_token_repository.NotificationService.send_notification')
    @patch('repository.fcm_token_repository.session_scope')
    def test_notify_user_with_user_id(self, mock_session_scope, mock_send_notification, mock_initialize_app, mock_certificate):

        # Mock the session and query
        mock_session = MagicMock()
        mock_query = mock_session.query.return_value
        mock_session_scope.return_value.__enter__.return_value = mock_session

        # Create a mock FCMToken object
        mock_fcm_token = FCMToken(
            user_id=6,
            fcm_token="mock_token_1",
            device_type="android",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_active=True
        )

        # Simulate tokens found in the database
        mock_query.filter_by.return_value.all.return_value = [mock_fcm_token]

        # Instantiate the repository and call notify_user with user_id
        fcm_token_repo = FCMTokenRepository()
        fcm_token_repo.notify_user(user_id=6, fcm_token_list=None, title="Test Title", body="Test Body")

        # Assert get_fcm_token was called
        mock_query.filter_by.assert_called_once_with(user_id=6)

        # Assert send_notification was called with correct arguments
        mock_send_notification.assert_called_once_with(
            ['mock_token_1'], "Test Title", "Test Body", None
        )

    # Test case when both user_id and fcm_token_list are None
    def test_notify_user_missing_arguments(self):
        # Instantiate the repository
        fcm_token_repo = FCMTokenRepository()

        # Call notify_user without user_id or fcm_token_list
        with self.assertRaises(ValueError) as context:
            fcm_token_repo.notify_user(user_id=None, fcm_token_list=None, title="Test Title", body="Test Body")

        # Assert that the correct exception is raised
        self.assertEqual(str(context.exception), "Either user_id or fcm_token_list must be provided")


if __name__ == '__main__':
    unittest.main()
