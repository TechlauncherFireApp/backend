"""Test Case 1: Successful Deletion
Input: user_id, event_id of an existing event that the user has permission to delete.
Expected Output: HTTP status code 200 with a success message.

Test Case 2: Event Not Found
Input: user_id, event_id of a non-existing event.
Expected Output: HTTP status code 404 with a message indicating the event was not found.

Test Case 3: Unauthorized User
Input: user_id of a non-authorized user, event_id of an existing event.
Expected Output: HTTP status code 403 Forbidden or 404 Not Found with a message indicating the user is not authorized to delete the event.

Test Case 4: Invalid Input Parameters
Input: Invalid or missing user_id or event_id.
Expected Output: HTTP status code 400 Bad Request with an appropriate error message.

Test Case 5: Internal Server Error
Input: When an unexpected exception occurs during event deletion.
Expected Output: HTTP status code 500 Internal Server Error with a message indicating the server error.

Test Case 6: User with ROOT_ADMIN Role
Input: user_id of a user with ROOT_ADMIN role, event_id of an existing event.
Expected Output: Successful deletion of the event with HTTP status code 200.

Test Case 7: User with other Roles
Input: user_id of a user with a role other than ROOT_ADMIN, event_id of an existing event.
Expected Output: HTTP status code 403 Forbidden with a message indicating that the user does not have permission to delete the event.

Test Case 8: Attempt to Delete Already Deleted Event
Input: user_id, event_id of an event that has already been deleted.
Expected Output: HTTP status code 404 with a message indicating the event was not found.

Test Case 9: Attempt to Delete Event without Required Permissions
Input: user_id, event_id of an event that the user has permission to view but not delete.
Expected Output: HTTP status code 403 Forbidden with a message indicating the user does not have permission to delete the event.
"""


payload_1 = {
        "title": "Test Event",
        "periodicity": 0,
        "start": "2024-05-02T00:00:00Z",
        "end": "2024-05-02T23:59:59Z"
    }

def test_delete_volunteer_unavailability_success(test_client, create_user):
    user_id = create_user
    test_client.post(f"/v2/volunteers/{user_id}/unavailability",
                     json=payload_1
                     )
    # Extract the event ID from the response
    event_id = (test_client.post(f"/v2/events/{user_id}/unavailability")).json["event_id"]

    # Make a DELETE request using the extracted event ID
    response = test_client.delete(f"/v2/volunteers/{user_id}/unavailability/{event_id}")

    assert response.status_code == 200



