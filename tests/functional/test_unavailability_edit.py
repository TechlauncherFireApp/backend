def test_update_unavailability_successful(test_client, create_user):
    user_id = create_user
    payload_1 = {
        "title": "All Day Event",
        "periodicity": 0,
        "start": "2024-05-02T00:00:00Z",
        "end": "2024-05-02T23:59:59Z"
    }
    create_response = test_client.post(f"/v2/volunteers/{user_id}/unavailability",
                     json=payload_1
                     )
    event_id = create_response.json['eventId']
    new_details = {
        "title": "Updated Event",
        "start": "2024-05-03T00:00:00Z",
        "end": "2024-05-03T23:59:59Z",
        "periodicity": 1
    }
    edit_response = test_client.put(f"/v2/volunteers/{user_id}/unavailability/{event_id}",
                               json=new_details)
    assert create_response.status_code == 200
    assert edit_response.status_code == 200
    assert edit_response.json == {"message": "Updated successfully"}

# 出现edit输入的和原本信息相同时 弹出什么提醒？
# 如果请求为空，弹出什么提醒

def test_update_unavailability_event_not_found(test_client, create_user):
    user_id = create_user
    event_id = -1
    new_details = {
        "title": "Nonexistent Event",
        "start": "2024-10-03T00:00:00Z",
        "end": "2024-10-03T23:59:59Z"
    }
    edit_response = test_client.put(f"/v2/volunteers/{user_id}/unavailability/{event_id}",
                               json=new_details)
    assert edit_response.status_code == 404
    # assert response.json == {"message": f"Event {event_id} can not be found"}

def test_update_unavailability_with_invalid_data_endtime_earlier_than_starttime(test_client, create_user):
    user_id = create_user
    payload_1 = {
        "title": "All Day Event",
        "periodicity": 0,
        "start": "2024-05-02T00:00:00Z",
        "end": "2024-05-02T23:59:59Z"
    }
    create_response = test_client.post(f"/v2/volunteers/{user_id}/unavailability",
                                       json=payload_1
                                       )
    event_id = create_response.json['eventId']
    invalid_details = {
        "title": "Invalid Time Range",
        "start": "2024-05-04T00:00:00Z",  # Start time is after the end time
        "end": "2024-05-03T23:59:59Z"
    }
    edit_response = test_client.put(f"/v2/volunteers/{user_id}/unavailability/{event_id}",
                               json=invalid_details)
    assert create_response.status_code == 200
    assert edit_response.status_code == 400
    # assert edit_response.json == {"message": "Invalid argument from the payload"}

def test_update_unavailability_with_invalid_data_starttime_in_the_past(test_client, create_user):
    user_id = create_user
    payload_1 = {
        "title": "All Day Event",
        "periodicity": 0,
        "start": "2024-05-02T00:00:00Z",
        "end": "2024-05-02T23:59:59Z"
    }
    create_response = test_client.post(f"/v2/volunteers/{user_id}/unavailability",
                                       json=payload_1
                                       )
    event_id = create_response.json['eventId']
    invalid_details = {
        "title": "Invalid Start Time",
        "start": "2024-03-04T00:00:00Z",
    }
    edit_response = test_client.put(f"/v2/volunteers/{user_id}/unavailability/{event_id}",
                               json=invalid_details)
    assert create_response.status_code == 200
    assert edit_response.status_code == 400
    # assert edit_response.json == {"message": "Invalid argument from the payload"}

def test_update_unavailability_with_invalid_data_endtime_in_the_past(test_client, create_user):
    user_id = create_user
    payload_1 = {
        "title": "Two Months Event",
        "periodicity": 0,
        "start": "2024-03-02T00:00:00Z",
        "end": "2024-05-02T23:59:59Z"
    }
    create_response = test_client.post(f"/v2/volunteers/{user_id}/unavailability",
                                       json=payload_1
                                       )
    event_id = create_response.json['eventId']
    invalid_details = {
        "title": "Invalid Start Time",
        "end": "2024-03-05T00:00:00Z",
    }
    edit_response = test_client.put(f"/v2/volunteers/{user_id}/unavailability/{event_id}",
                               json=invalid_details)
    assert create_response.status_code == 200
    assert edit_response.status_code == 400
    # assert edit_response.json == {"message": "Invalid argument from the payload"}