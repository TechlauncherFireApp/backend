from datetime import datetime, timezone
from unittest.mock import patch
from services.jwk import JWKService
from repository import volunteer_unavailability_v2

"""
Test Case 6: User with ROOT_ADMIN Role
Input: user_id of a user with ROOT_ADMIN role, event_id of an existing event.
Expected Output: Successful deletion of the event with HTTP status code 200.

Test Case 7: User with other Roles
Input: user_id of a user with a role other than ROOT_ADMIN, event_id of an existing event.
Expected Output: HTTP status code 403 Forbidden with a message indicating that the user does not have permission to delete the event.



Test Case 9: Attempt to Delete Event without Required Permissions
Input: user_id, event_id of an event that the user has permission to view but not delete.
Expected Output: HTTP status code 403 Forbidden with a message indicating the user does not have permission to delete the event.
"""

payload = {
    "title": "Test Event",
    "periodicity": 0,
    "start": "2025-05-02T00:00:00Z",
    "end": "2025-05-02T23:59:59Z"
}

"""Test Case 1: Successful Deletion
Input: user_id, event_id of an existing event that the user has permission to delete.
Expected Output: HTTP status code 200 with a success message."""


def test_delete_volunteer_unavailability_success(test_client, create_user):
    user_id = create_user
    event_response = test_client.post(f"/v2/volunteers/{user_id}/unavailability",
                                      json=payload
                                      )
    # checks body was posted correctly
    assert event_response.status_code == 200

    # extract event_id
    event_id = event_response.json["eventId"]

    # make delete request
    response = test_client.delete(f"/v2/volunteers/{user_id}/unavailability/{event_id}")

    assert response.status_code == 200


"""Test Case 2: Event Not Found
Input: user_id, event_id of a non-existing event.
Expected Output: HTTP status code 404 with a message indicating the event was not found."""


def test_delete_event_not_found(test_client, create_user):
    user_id = create_user
    event_response = test_client.post(f"/v2/volunteers/{user_id}/unavailability",
                                      json=payload
                                      )

    assert event_response.status_code == 200
    # extract event_id
    event_id = event_response.json["eventId"]

    response = test_client.delete(f"/v2/volunteers/{user_id}/unavailability/{event_id + 1}")

    assert response.status_code == 404


"""Test Case 3: Attempt to Delete Already Deleted Event
Input: user_id, event_id of an event that has already been deleted.
Expected Output: HTTP status code 404 with a message indicating the event was not found."""


def test_delete_event_already_deleted(test_client, create_user):
    user_id = create_user
    event_response = test_client.post(f"/v2/volunteers/{user_id}/unavailability", json=payload)
    assert event_response.status_code == 200
    event_id = event_response.json["eventId"]
    response = test_client.delete(f"/v2/volunteers/{user_id}/unavailability/{event_id}")
    assert response.status_code == 200
    response_repeat = test_client.delete(f"/v2/volunteers/{user_id}/unavailability/{event_id}")
    assert response_repeat.status_code == 404


# """Test Case 4: Unauthorized User Input: user_id of a non-authorized user, event_id of an existing event.
# Expected Output: HTTP status code 403 Forbidden or 404 Not Found with a message indicating the user is not authorized to
# delete the event."""


# def test_delete_unauthorized(test_client, create_user1, create_user2):
#     # Create the first user and post an unavailability event
#     user_id1 = create_user1
#     event_response = test_client.post(f"/v2/volunteers/{user_id1}/unavailability",
#                                       json=payload)
#     assert event_response.status_code == 200
#
#     # Extract the event ID
#     event_id = event_response.json()["eventId"]
#
#     # Create the second user
#     user_id2 = create_user2
#
#     # Generate a valid JWT token for user_id1
#     token = JWKService.generate(user_id1, "user1", "admin",
#                                 datetime.now(), datetime.now())
#
#     # Attempt to delete the event created by user_id1 using the credentials of user_id2
#     response = test_client.delete(f"/v2/volunteers/{user_id2}/unavailability/{event_id}",
#                                   headers={"Authorization": f"Bearer {token}"})
#
#     # Ensure that the unauthorized user receives a 401 Forbidden status code
#     assert response.status_code == 401


"""Test Case 4: Internal Server Error
Input: When an unexpected exception occurs during event deletion.
Expected Output: HTTP status code 500 Internal Server Error with a message indicating the server error."""


def test_internal_server_error(test_client, create_user):
    user_id = create_user
    event_response = test_client.post(f"/v2/volunteers/{user_id}/unavailability", json=payload)
    assert event_response.status_code == 200
    # extract event_id
    event_id = event_response.json["eventId"]

    # Simulate an unexpected exception during event deletion
    # Patch the remove_event method to raise an exception
    with patch("repository.volunteer_unavailability_v2.EventRepository.remove_event") as mock_remove_event:
        mock_remove_event.side_effect = Exception("Something went wrong")

        # Send a delete request
        response = test_client.delete(f"/v2/volunteers/{user_id}/unavailability/{event_id}")

    # Ensure that the response status code is 500 Internal Server Error
    assert response.status_code == 500
