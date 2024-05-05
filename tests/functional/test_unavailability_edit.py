from datetime import datetime, timedelta

now = datetime.now()
def test_update_unavailability_successful(test_client, create_user):
    user_id = create_user
    start = now + timedelta(days=1)
    end = start + timedelta(hours=23, minutes=59, seconds=59)
    payload_1 = {
        "title": "All Day Event",
        "periodicity": 0,
        "start": start.isoformat(),
        "end": end.isoformat()
    }
    create_response = test_client.post(f"/v2/volunteers/{user_id}/unavailability",
                     json=payload_1
                     )
    event_id = create_response.json['eventId']
    new_details = {
        "title": "Updated Event",
        "start": (start + timedelta(days=1)).isoformat(),
        "end": (end + timedelta(days=1)).isoformat(),
        "periodicity": 1
    }
    edit_response = test_client.put(f"/v2/volunteers/{user_id}/unavailability/{event_id}",
                               json=new_details)
    assert create_response.status_code == 200
    assert edit_response.status_code == 200
    assert edit_response.json == {"message": "Updated successfully"}


def test_update_unavailability_event_not_found(test_client, create_user):
    user_id = create_user
    event_id = -1
    start = now + timedelta(days=10)
    end = start + timedelta(hours=23, minutes=59, seconds=59)
    new_details = {
        "title": "Nonexistent Event",
        "start": start.isoformat(),
        "end": end.isoformat()
    }
    edit_response = test_client.put(f"/v2/volunteers/{user_id}/unavailability/{event_id}",
                               json=new_details)
    assert edit_response.status_code == 404
    # assert response.json == {"message": f"Event {event_id} can not be found"}

def test_update_unavailability_with_invalid_data_changeboth_endtime_earlier_than_starttime(test_client, create_user):
    user_id = create_user
    start = now + timedelta(days=1)
    end = start + timedelta(hours=23, minutes=59, seconds=59)
    payload_1 = {
        "title": "All Day Event",
        "periodicity": 0,
        "start": start.isoformat(),
        "end": end.isoformat()
    }
    create_response = test_client.post(f"/v2/volunteers/{user_id}/unavailability",
                                       json=payload_1
                                       )
    event_id = create_response.json['eventId']
    invalid_details = {
        "title": "Invalid Time Range",
        "start": (start + timedelta(days=3)).isoformat(), # start time is later than end time
        "end": (end + timedelta(days=1)).isoformat()
    }
    edit_response = test_client.put(f"/v2/volunteers/{user_id}/unavailability/{event_id}",
                               json=invalid_details)
    assert create_response.status_code == 200
    assert edit_response.status_code == 400
    # assert edit_response.json == {"message": "Invalid argument from the payload"}

def test_update_unavailability_with_invalid_data_changestart_endtime_earlier_than_starttime(test_client, create_user):
    user_id = create_user
    start = now + timedelta(days=1)
    end = start + timedelta(hours=23, minutes=59, seconds=59)
    payload_1 = {
        "title": "All Day Event",
        "periodicity": 0,
        "start": start.isoformat(),
        "end": end.isoformat()
    }
    create_response = test_client.post(f"/v2/volunteers/{user_id}/unavailability",
                                       json=payload_1
                                       )
    event_id = create_response.json['eventId']
    invalid_details = {
        "title": "Invalid Start time for Later than Original End Time",
        "start": (start + timedelta(days=3)).isoformat()
    }
    edit_response = test_client.put(f"/v2/volunteers/{user_id}/unavailability/{event_id}",
                               json=invalid_details)
    assert create_response.status_code == 200
    assert edit_response.status_code == 400
    # assert edit_response.json == {"message": "Invalid argument from the payload"}

def test_update_unavailability_with_invalid_data_changeend_endtime_earlier_than_starttime(test_client, create_user):
    user_id = create_user
    start = now + timedelta(days=2)
    end = start + timedelta(hours=23, minutes=59, seconds=59)
    payload_1 = {
        "title": "All Day Event",
        "periodicity": 0,
        "start": start.isoformat(),
        "end": end.isoformat()
    }
    create_response = test_client.post(f"/v2/volunteers/{user_id}/unavailability",
                                       json=payload_1
                                       )
    event_id = create_response.json['eventId']
    invalid_details = {
        "title": "Invalid End time for Earlier than Original Start Time",
        "end": (start - timedelta(days=1)).isoformat()
    }
    edit_response = test_client.put(f"/v2/volunteers/{user_id}/unavailability/{event_id}",
                                    json=invalid_details)
    assert create_response.status_code == 200
    assert edit_response.status_code == 400
    # assert edit_response.json == {"message": "Invalid argument from the payload"}

def test_update_unavailability_with_invalid_data_starttime_in_the_past(test_client, create_user):
    user_id = create_user
    start = now + timedelta(days=2)
    end = start + timedelta(hours=23, minutes=59, seconds=59)
    payload_1 = {
        "title": "All Day Event",
        "periodicity": 0,
        "start": start.isoformat(),
        "end": end.isoformat()
    }
    create_response = test_client.post(f"/v2/volunteers/{user_id}/unavailability",
                                       json=payload_1
                                       )
    event_id = create_response.json['eventId']
    invalid_details = {
        "title": "Meaningless Start Time",
        "start": (now - timedelta(days=1)).isoformat()
    }
    edit_response = test_client.put(f"/v2/volunteers/{user_id}/unavailability/{event_id}",
                               json=invalid_details)
    assert create_response.status_code == 200
    assert edit_response.status_code == 400
    # assert edit_response.json == {"message": "Invalid argument from the payload"}

def test_update_unavailability_with_invalid_data_endtime_in_the_past(test_client, create_user):
    user_id = create_user
    start = now - timedelta(days=10)
    end = now + timedelta(days=10)
    payload_1 = {
        "title": "Twenty Days Event",
        "periodicity": 0,
        "start": start.isoformat(),
        "end": end.isoformat()
    }
    create_response = test_client.post(f"/v2/volunteers/{user_id}/unavailability",
                                       json=payload_1
                                       )
    event_id = create_response.json['eventId']
    invalid_details = {
        "title": "Meaningless End Time",
        "end": (now - timedelta(days=1)).isoformat()
    }
    edit_response = test_client.put(f"/v2/volunteers/{user_id}/unavailability/{event_id}",
                               json=invalid_details)
    assert create_response.status_code == 200
    assert edit_response.status_code == 400
    # assert edit_response.json == {"message": "Invalid argument from the payload"}