from domain import UnavailabilityTime, MergedUnavailabilityTime, session_scope
import json

# doesn't consider periodicity
# have problem, can't run successfully now

def merge_intervals(session):
    user_ids = session.query(UnavailabilityTime.userId).distinct().all()
    user_ids = [uid[0] for uid in user_ids]

    for user_id in user_ids:
        events = session.query(UnavailabilityTime).filter_by(UnavailabilityTime.userId == user_id,
                                                             UnavailabilityTime.status == 1)\
                                                  .order_by(UnavailabilityTime.start).all()
        if not events:
            continue

        merged = []
        merged_eventIds = []
        merged_titles = []
        start_times = []
        end_times = []

        for event in events:
            # if there's no event in the list or if the else events for this user will not be overlap with the existing one
            # then the new merged event can be reset
            if not merged or merged[0].end < event.start:
                # the event is complete merged event, it can be saved
                if merged:
                    save_merged_event(session, merged, merged_eventIds, merged_titles, start_times, end_times)
                # reset merged event information
                merged = [event]
                merged_eventIds = [str(event.eventId)]
                merged_titles = [event.title]
                start_times = [event.start]
                end_times = [event.end]
            else:
                # have new overlapping event and need to update the merged information
                # the last event in merged list is a merged one
                merged[0].end = max(merged[0].end, event.end)
                merged_eventIds.append(str(event.eventId))
                merged_titles.append(event.title)
                start_times.append(event.start)
                end_times.append(event.end)

        # save the last merged event
        if merged:
            save_merged_event(session, merged, merged_eventIds, merged_titles, start_times, end_times)

    session.commit()

def save_merged_event(session, merged_events, eventIds, titles, start_times, end_times):
    time_intervals = [
        {"start": start.isoformat(), "end": end.isoformat()} for start, end in zip(start_times, end_times)
    ]

    new_event = MergedUnavailabilityTime(
        userId=merged_events[0].userId,
        mergedEventId=json.dumps(eventIds),
        mergedTitle=json.dumps(titles),
        mergedTimeInterval=json.dumps(time_intervals),
        start=merged_events[0].start,
        end=merged_events[0].end
    )
    session.add(new_event)

def main():
    with session_scope() as session:
        merge_intervals(session)

if __name__ == "__main__":
    main()
