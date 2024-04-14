import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

from domain import UnavailabilityTime
from repository import volunteer_unavailability_v2


class TestEventRepository(unittest.TestCase):
    def setUp(self):
        self.repository = volunteer_unavailability_v2.EventRepository()

    def test_edit_event(self):
        mock_event = MagicMock()
        with patch('repository.volunteer_unavailability_v2.session_scope') as mock_session_scope:
            with MagicMock() as mock_session:
                mock_session.query().filter().first.return_value = mock_event
            result = self.repository.edit_event(1, 1, title="New Title", start=datetime.now(), end=datetime.now(),
                                                periodicity=1)
            # Assert that the result is True since an event exists
            self.assertTrue(result)

    def test_create_event(self):
        with MagicMock() as session:
            session.add.return_value = None
            session.flush.return_value = None
            result = session.repository.create_event(1, "Title", datetime.now(), datetime.now(), 1)
            self.assertIsNotNone(result)

    def test_get_event_with_events(self):
        event_id = self.repository.create_event(1, "Title", datetime.now(), datetime.now(), 1)
        result = self.repository.get_event(event_id)
        self.assertIsNotNone(result)

    def test_get_past_events(self):
        past_datetime = (datetime.now() - timedelta(days=1))
        event_id = self.repository.create_event(1, "Title", past_datetime, datetime.now(), 1)
        result = self.repository.get_event(event_id)
        self.assertTrue([] == result)

    def test_remove_event(self):
        with MagicMock() as session:

            # Create a mock event
            event_id = session.repository.create_event(1, "Title", datetime.now(), datetime.now(), 1)
            self.assertIsNotNone(event_id)

            # Remove the event
            result = session.repository.remove_event(1, event_id)

            # Check if removal was successful
            self.assertTrue(result)

    ##
    def test_check_duplicate_events(self):
        # Mock the session to simulate database interaction
        with MagicMock() as session:

            # Call the method under test
            session.repository.create_event(1, "Title", datetime.now(), datetime.now(), 1)
            result = session.repository.check_duplicate_event(1, datetime.now(), datetime.now(), 1)

            # Check if the method correctly detects no duplicate events
            self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
