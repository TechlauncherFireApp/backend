import json
import logging

from flask import jsonify

from datetime import datetime, timezone
from exception import EventNotFoundError, InvalidArgumentError
from domain import UnavailabilityTime, session_scope, MergedUnavailabilityTime
from repository.merge_volunteer_unavailability_v2 import save_merged_event


class EventRepository:
    def __init__(self):
        pass

    def edit_event(self, session, userId, eventId, title=None, start=None, end=None, periodicity=None):
        now = datetime.now()
        event = session.query(UnavailabilityTime).filter(UnavailabilityTime.eventId == eventId,
                                                         UnavailabilityTime.userId == userId,
                                                         UnavailabilityTime.status != 0).first()
        if event is None:
            raise EventNotFoundError(eventId)
        actual_start = start if start is not None else event.start
        actual_end = end if end is not None else event.end
        if actual_end < actual_start:
            raise InvalidArgumentError("The end time must not be before the start time.")
        if actual_start < now:
            raise InvalidArgumentError("The start time must not be in the past.")
        if actual_end < now:
            raise InvalidArgumentError("The end time must not be in the past.")
        # Edit fields with new values
        event.start = actual_start
        event.end = actual_end
        if title is not None:
            event.title = title
        if periodicity is not None:
            event.periodicity = periodicity
        session.commit()
        # store the event version that after editing(for merging)
        new_event = session.query(UnavailabilityTime).filter(UnavailabilityTime.eventId == eventId,
                                                             UnavailabilityTime.userId == userId,
                                                             UnavailabilityTime.status != 0).first()
        # update merged table when edit a record
        self.update_merged_events_on_edit(session, userId, new_event)

    def get_event(self, userId):
        """
        get all the non-availability events of the given user
        :param userId: Integer, user id, who want to query the events
        """
        now = datetime.now()
        with session_scope() as session:
            try:
                # only show the unavailability time that is end in the future
                events = session.query(UnavailabilityTime).filter(
                    UnavailabilityTime.userId == userId, UnavailabilityTime.status == 1,
                    UnavailabilityTime.end > now).all()
                if events:
                    event_records = []
                    for event in events:
                        # write unavailability information into list
                        event_record = {
                            "eventId": event.eventId,
                            "userId": event.userId,
                            "title": event.title,
                            "startTime": event.start.isoformat(),
                            "endTime": event.end.isoformat(),
                            "periodicity": event.periodicity
                        }
                        event_records.append(event_record)
                    return event_records
                else:
                    return []
            except Exception as e:
                logging.error(e)
                return None

    # copy from repository.unavailability_repository.py
    def create_event(self, userId, title, startTime, endTime, periodicity):
        """
        Function to create an event
        :param session: session
        :param userId: Integer, user id
        :param title: String, reason why unavailable
        :param startTime: DateTime, from what time is unavailable
        :param endTime: DateTime, to what time is unavailable
        :param periodicity: Integer, Daily = 1, Weekly = 2, One-Off = 3
        """
        event = UnavailabilityTime(userId=userId, title=title, start=startTime, end=endTime,
                                   periodicity=periodicity)
        with session_scope() as session:
            session.add(event)
            # session.expunge(question)
            session.flush()
            # update merged table when create a new record
            self.update_merged_events_on_create(session,userId,event)
            return event.eventId

    # copy from repository.unavailability_repository.py
    def remove_event(self, userId, eventId):
        """
        Function to remove an event
        :param session: session
        :param userId: Integer, user id, who want to remove an event
        :param eventId: Integer, event id want to remove
        :return: True: remove successful
                 False: remove failed
        """
        with session_scope() as session:
            existing = session.query(UnavailabilityTime).filter(UnavailabilityTime.userId == userId,
                                                                UnavailabilityTime.eventId == eventId).first()
            if existing is not None and existing.status is True:
                existing.status = False
                # update merged table when delete a record
                self.update_merged_events_on_delete(session,eventId,userId)
                return True
            return False

    # checks via base value comparison, returns the event Ids of overlapped events
    def check_overlapping_events(self, userId, startTime, endTime, periodicity):
        with session_scope() as session:
            # checks if new time frame overlaps with any existing in the database for specific userId
            overlapping_events = session.query(UnavailabilityTime).filter(
                UnavailabilityTime.userId == userId,
                UnavailabilityTime.start < endTime,
                UnavailabilityTime.end > startTime,
                UnavailabilityTime.periodicity == periodicity
            ).all()
            # Convert overlapping events to a list of dictionaries
            overlapping_details = []
            for event in overlapping_events:
                overlapping_details.append({
                    "eventId": event.eventId,
                    # Add any other attributes you need
                })

        return overlapping_details

    def check_duplicate_event(self, userId, startTime, endTime, periodicity):
        with session_scope() as session:
            # Query the database for events with the same start time, end time, and periodicity
            duplicate_events_count = session.query(UnavailabilityTime).filter(
                UnavailabilityTime.userId == userId,
                UnavailabilityTime.start == startTime,
                UnavailabilityTime.end == endTime,
                UnavailabilityTime.periodicity == periodicity,
                UnavailabilityTime.status != 0
            ).count()

        # If the count of duplicate events is greater than 0, duplicates exist, return True
        return duplicate_events_count > 0

    def check_overlapping_events_for_merged(self, session, userId, startTime, endTime):
        # checks if new time frame overlaps with any existing in the database for specific userId
        overlapping_events = session.query(MergedUnavailabilityTime).filter(
            MergedUnavailabilityTime.userId == userId,
            MergedUnavailabilityTime.start <= endTime,
            MergedUnavailabilityTime.end >= startTime
        ).all()
        return overlapping_events

    def update_merged_events_on_create(self, session, userId, new_event):
        # Step 1: Check for overlapping events
        overlapping_events = self.check_overlapping_events_for_merged(session, userId, new_event.start, new_event.end)
        # If no overlapping events, create a new record directly
        if not overlapping_events:
            overlapping_events = []
        # Initialize lists for merged data
        new_merged_event_ids = [str(new_event.eventId)]
        new_merged_titles = [new_event.title]
        new_merged_time_intervals = [{'start': new_event.start.isoformat(), 'end': new_event.end.isoformat()}]
        min_start = new_event.start
        max_end = new_event.end
        # Step 2: merge the new events and the overlapping merged events
        for event in overlapping_events:
            event_ids = json.loads(event.mergedEventId)
            titles = json.loads(event.mergedTitle)
            time_intervals = json.loads(event.mergedTimeInterval)
            new_merged_event_ids += event_ids
            new_merged_titles += titles
            new_merged_time_intervals += time_intervals
            if event.start < min_start:
                min_start = event.start
            if event.end > max_end:
                max_end = event.end
        # Step 3: Create new merged record
        new_merged_record = MergedUnavailabilityTime(
            userId=userId,
            mergedEventId=json.dumps(new_merged_event_ids),
            mergedTitle=json.dumps(new_merged_titles),
            mergedTimeInterval=json.dumps(new_merged_time_intervals),
            start=min_start,
            end=max_end
        )
        session.add(new_merged_record)
        try:
            # Step 4: Delete old merged records
            for record in overlapping_events:
                session.delete(record)
            # Commit all changes
            session.commit()
        except Exception as e:
            session.rollback()  # Rollback if any exception occurs
            raise e

    def update_merged_events_on_delete(self, session, deleted_eventId, userId):
        # Step 1: Find the merged records containing the deleted eventId
        affected_record = session.query(MergedUnavailabilityTime).filter(
            MergedUnavailabilityTime.userId == userId,
            MergedUnavailabilityTime.mergedEventId.contains(str(deleted_eventId))
        ).first()
        # Step 2: Modified the information of affected merged event
        event_ids = json.loads(affected_record.mergedEventId)
        titles = json.loads(affected_record.mergedTitle)
        time_intervals = json.loads(affected_record.mergedTimeInterval)
        # Step 3: Add the new merged records and delete the old affected one
        # If the record contains only one eventId (not overlapping in unavailabilityTime table), just delete this record in mergedUnavailabilityTime table
        if len(event_ids) > 1:
            # Remove the deleted event details from the record
            index = event_ids.index(str(deleted_eventId))
            del event_ids[index]
            del titles[index]
            del time_intervals[index]
            # Redo the merging for the rest events in this event_ids
            event_ids = [int(id) for id in event_ids]
            events = session.query(UnavailabilityTime).filter(UnavailabilityTime.userId == userId,
                                                              UnavailabilityTime.eventId.in_(event_ids)) \
                                                      .order_by(UnavailabilityTime.start).all()
            self.redo_merged_intervals(session, events)
        # Delete the old one
        session.delete(affected_record)
        # Step 4: Commit changes
        try:
            session.commit()
        except Exception as e:
            session.rollback()
            raise Exception("Failed to update merged records on event deletion: {}".format(str(e)))

    def update_merged_events_on_edit(self, session, userId, new_event):
        # Step 1: Find merged records containing the old event ID
        affected_record = session.query(MergedUnavailabilityTime).filter(
            MergedUnavailabilityTime.userId == userId,
            MergedUnavailabilityTime.mergedEventId.contains(str(new_event.eventId))
        ).first()
        # Step 2: Recheck the overlapping between the new event and other events and redo the merging, then delete the merged records which is remerged in merged table
        event_ids = json.loads(affected_record.mergedEventId)
        titles = json.loads(affected_record.mergedTitle)
        time_intervals = json.loads(affected_record.mergedTimeInterval)
        # if the edited one is a not merged record in mergedUnavailabilityTime table, then just delete the origin one and then do as create operation
        if len(event_ids) == 1:
            # Delete the merged record if it only contains this event
            session.delete(affected_record)
            self.update_merged_events_on_create(session, userId, new_event)
        else:
            # Update the merged record by removing the old event
            index = event_ids.index(str(new_event.eventId))
            del event_ids[index]
            del titles[index]
            del time_intervals[index]
            # Get the events for the unavailability events which is overlap with the new_event(after edit) and also store new_event here
            # To use this list for redo_merged_intervals
            overlapping_events = session.query(UnavailabilityTime).filter(
                UnavailabilityTime.userId == userId,
                UnavailabilityTime.start <= new_event.end,
                UnavailabilityTime.end >= new_event.start,
                UnavailabilityTime.periodicity == new_event.periodicity
            ).all()
            overlapping_events.append(new_event)
            # Get the eventId of some merged events which is overlapped with the new_event to delete them
            overlapping_merged_events = self.check_overlapping_events_for_merged(session, userId, new_event.start, new_event.end)
            # redo mergeing for these overlapping events
            self.redo_merged_intervals(session, overlapping_events)
            for event in overlapping_merged_events:
                session.delete(event)
            session.delete(affected_record)
        # Step 3: Commit changes
        try:
            session.commit()
        except Exception as e:
            session.rollback()
            raise e

    def redo_merged_intervals(self, session, events):
        merged = []
        merged_eventIds = []
        merged_titles = []
        start_times = []
        end_times = []

        for event in events:
            # if there's no event in the merged list or if the else events for this user will not be overlap with the existing one
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