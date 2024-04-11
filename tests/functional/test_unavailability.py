def test_create_unavailability_consecutive_event_id(test_client, create_user):
    user_id = create_user
    payload_1 = {
        "title": "All Day Event",
        "periodicity": 0,
        "start": "2024-03-02T00:00:00Z",
        "end": "2024-03-02T23:59:59Z"
    }
    payload_2 = {
        "title": "All Day Event",
        "periodicity": 0,
        "start": "2024-03-03T00:00:00Z",
        "end": "2024-03-03T23:59:59Z"
    }
    response = test_client.post(f"/v2/volunteers/{user_id}/unavailability",
                                json=payload_1
                                )
    response_2 = test_client.post(f"/v2/volunteers/{user_id}/unavailability",
                                  json=payload_2
                                  )
    assert response.status_code == 200
    assert response_2.status_code == 200
    assert response_2.json["eventId"] - response.json["eventId"] == 1


# def test_create_unavailability_same_time_interval(test_client, create_user):
#     user_id = create_user
#     payload = {
#         "title": "All Day Event",
#         "periodicity": 0,
#         "start": "2024-03-02T00:00:00Z",
#         "end": "2024-03-02T23:59:59Z"
#     }
#     response = test_client.post(f"/v2/volunteers/{user_id}/unavailability",
#                                 json=payload
#                                 )
#     response_2 = test_client.post(f"/v2/volunteers/{user_id}/unavailability",
#                                   json=payload
#                                   )
#     print(response.json)
#
#     assert response.status_code == 200
#     assert response_2.status_code == 400


def test_create_unavailability_nonexistent_user_id(test_client):
    user_id = -1
    payload = {
        "title": "All Day Event",
        "periodicity": 0,
        "start": "2024-03-02T00:00:00Z",
        "end": "2024-03-02T23:59:59Z"
    }
    response = test_client.post(f"/v2/volunteers/{user_id}/unavailability",
                                json=payload
                                )
    assert response.status_code == 500


def test_create_unavailability_end_before_start(test_client, create_user):
    user_id = create_user
    payload = {
        "title": "All Day Event",
        "periodicity": 0,
        "start": "2024-03-02T00:00:00Z",
        "end": "2024-03-01T23:59:59Z"
    }
    response = test_client.post(f"/v2/volunteers/{user_id}/unavailability",
                                json=payload
                                )
    assert response.status_code == 400


# def test_create_unavailability_overlapped_time(test_client, create_user):
#     user_id = create_user
#     payload_1 = {
#         "title": "All Day Event",
#         "periodicity": 0,
#         "start": "2024-03-03T00:00:00Z",
#         "end": "2024-03-04T23:59:59Z"
#     }
#     payload_2 = {
#         "title": "All Day Event",
#         "periodicity": 0,
#         "start": "2024-03-01T00:00:00Z",
#         "end": "2024-03-05T23:59:59Z"
#     }
#     response_1 = test_client.post(f"/v2/volunteers/{user_id}/unavailability",
#                                   json=payload_1
#                                   )
#     response_2 = test_client.post(f"/v2/volunteers/{user_id}/unavailability",
#                                   json=payload_2
#                                   )
#     assert response_1.status_code == 200
#     assert response_2.status_code == 400


# def test_merge_overlapping_unavailability_intervals(test_client, create_user):
#     user_id = create_user
#     payload_1 = {
#         "title": "Morning Event",
#         "periodicity": 0,
#         "start": "2024-03-05T08:00:00Z",
#         "end": "2024-03-05T12:00:00Z"
#     }
#     payload_2 = {
#         "title": "Afternoon Event",
#         "periodicity": 0,
#         "start": "2024-03-05T11:00:00Z",
#         "end": "2024-03-05T15:00:00Z"
#     }
#     test_client.post(f"/v2/volunteers/{user_id}/unavailability", json=payload_1)
#     response = test_client.post(f"/v2/volunteers/{user_id}/unavailability", json=payload_2)
#     assert response.status_code == 200
#     assert len(response.json["mergedIntervals"]) == 1  # json response must have mergedIntervals field if it is merged
#     assert response.json["mergedIntervals"][0]["start"] == "2024-03-05T08:00:00Z"
#     assert response.json["mergedIntervals"][0]["end"] == "2024-03-05T15:00:00Z"
#
#
# def test_merge_adjacent_unavailability_intervals(test_client, create_user):
#     user_id = create_user
#     payload_1 = {
#         "title": "Morning Shift",
#         "periodicity": 0,
#         "start": "2024-03-06T08:00:00Z",
#         "end": "2024-03-06T12:00:00Z"
#     }
#     payload_2 = {
#         "title": "Afternoon Shift",
#         "periodicity": 0,
#         "start": "2024-03-06T12:00:00Z",
#         "end": "2024-03-06T16:00:00Z"
#     }
#     test_client.post(f"/v2/volunteers/{user_id}/unavailability", json=payload_1)
#     response = test_client.post(f"/v2/volunteers/{user_id}/unavailability", json=payload_2)
#     assert response.status_code == 200
#     assert len(response.json["mergedIntervals"]) == 1  # json response must have mergedIntervals field if it is merged
#     assert response.json["mergedIntervals"][0]["start"] == "2024-03-06T08:00:00Z"
#     assert response.json["mergedIntervals"][0]["end"] == "2024-03-06T16:00:00Z"
