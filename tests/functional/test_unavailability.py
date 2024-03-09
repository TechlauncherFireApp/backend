# Testing criteria:
# - two consecutive create operation must output two consecutive event_id
# - Cannot create two unavailability with the same time interval
# - Cannot create availability for nonexistent user_id
# - Cannot create unavailability with end time earlier than start time
# - Cannot create unavailability with weird periodicity (to be discussed)
# - There cannot be two unavailability from the same user with overlapped time interval
# - Merge interval (if implemented on API)
def test_create_unavailability_consecutive_eventId(test_client):
    userId = 49  # admin id
    payload = {
        "title": "All Day Event",
        "periodicity": 0,
        "start": "2024-03-02T00:00:00Z",
        "end": "2024-03-02T23:59:59Z"
    }
    response = test_client.post(f"/v2/volunteers/{userId}/unavailability",
                                json=payload
                                )
    assert response.status_code == 200

