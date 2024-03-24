# def test_get_volunteer_unavailability_success(test_client):
#     user_id = 49
#     payload_1 = {
#         "title": "All Day Event",
#         "periodicity": 0,
#         "start": "2024-03-02T00:00:00Z",
#         "end": "2024-03-02T23:59:59Z"
#     }
#     test_client.post(f"/v2/volunteers/{user_id}/unavailability",
#                      json=payload_1
#                      )
#
#     response = test_client.get(f"/v2/volunteers/{user_id}/unavailability")
#     assert response.status_code == 200


def test_get_volunteer_unavailability_no_records(test_client):
    user_id = 48  # Assuming this user has no unavailability records
    test_client.post(f"/v2/volunteers/{user_id}/unavailability")
    response = test_client.get(f"/v2/volunteers/{user_id}/unavailability")
    assert response.status_code == 400  # Assuming the endpoint returns a 400 status for no records found
    assert response.json == {"message": "No unavailability record found."}  # Expected response body for no records


# def test_get_volunteer_unavailability_invalid_user(test_client):
#     user_id = -1
#     payload = {
#         "title": "All Day Event",
#         "periodicity": 0,
#         "start": "2024-03-02T00:00:00Z",
#         "end": "2024-03-02T23:59:59Z"
#     }
#     test_client.post(f"/v2/volunteers/{user_id}/unavailability",
#                      json=payload
#                      )
#     response = test_client.get(f"/v2/volunteers/{user_id}/unavailability")
#     assert response.status_code == 404 # Assuming the system treats requests for non-existent users as bad requests
#     # or not found
#     assert response.json == {"message": "User not found"}  # Assuming this is the response for an invalid user ID
