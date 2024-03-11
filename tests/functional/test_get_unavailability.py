def test_get_volunteer_unavailability_success(test_client):
    user_id = 49  # Assuming this user has at least one unavailability record
    response = test_client.get(f"/v2/volunteers/{user_id}/unavailability")
    assert response.status_code == 200
    assert "unavailability" in response.json  # Assuming the response includes an 'unavailability' key
    assert isinstance(response.json["unavailability"],
                      list)  # Assuming the unavailability records are returned as a list


def test_get_volunteer_unavailability_no_records(test_client):
    user_id = 50  # Assuming this user has no unavailability records
    response = test_client.get(f"/v2/volunteers/{user_id}/unavailability")
    assert response.status_code == 400  # Assuming the endpoint returns a 400 status for no records found
    assert response.json == {'userID': user_id, 'success': False}  # Expected response body for no records


def test_get_volunteer_unavailability_invalid_user(test_client):
    user_id = -1  # Non-existent user ID
    response = test_client.get(f"/v2/volunteers/{user_id}/unavailability")
    # Assuming the system treats requests for non-existent users as bad requests or not found
    assert response.status_code == 404
    assert response.json == {"message": "User not found"}  # Assuming this is the response for an invalid user ID


# This is not yet implemented in the get method
def test_get_volunteer_unavailability_unauthorized(test_client):
    user_id = 30
    # This test assumes that the endpoint requires authentication and that the test client is not authenticated
    response = test_client.get(f"/v2/volunteers/{user_id}/unavailability")
    assert response.status_code == 401  # Unauthorized access
    assert "error" in response.json  # Checking for an error message in the response


# This is not yet implemented in the get method
def test_get_volunteer_unavailability_forbidden(test_client):
    user_id = 31
    # Assuming the test client is authenticated as a different user without permissions to access this user's data
    response = test_client.get(f"/v2/volunteers/{user_id}/unavailability")
    assert response.status_code == 403  # Forbidden access
    assert "error" in response.json  # Checking for an error message indicating lack of permissions
