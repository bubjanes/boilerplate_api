import os
import logging
import pickle
import json
from flask_restx import abort
from flask import current_app

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from datetime import datetime, timedelta, date, timezone
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse

logger = logging.getLogger(__name__)

TOKENS = {1: "token.pkl", 2: "token2.pkl"}

def get_service(hos_id):
    token_file = TOKENS[hos_id]
    credentials = pickle.load(open("turnero/turnos/tokens/" + token_file, "rb"))
    service = build("calendar", "v3", credentials=credentials, cache_discovery=False)
    return service


def get_event(calendar_id, event_id, hos_id):
    service = get_service(hos_id)
    event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
    return event


def check_attend(event):
    has_attend = False
    if "attendees" in event:
        has_attend = True
    return has_attend


def get_dates(calendar_id, hos_id):
    service = get_service(hos_id)
    event_date = {}
    event_dates = []
    readable_dates = []
    page_token = None

    date_today = datetime.now(timezone.utc).astimezone()
    timemin = date_today.isoformat()
    date_after_month = datetime.now(timezone.utc).astimezone() + relativedelta(weeks=12)
    timemax = date_after_month.isoformat()

    try:
        current_app.logger.info(
            "Attempting to GET appointments from Google Calendar API..."
        )
        while True:
            events = (
                service.events()
                .list(
                    calendarId=calendar_id,
                    pageToken=page_token,
                    timeMax=timemax,
                    timeMin=timemin,
                    timeZone="America/Argentina/Cordoba",
                    maxAttendees=1,
                    orderBy="startTime",
                    singleEvents=True
                )
                .execute()
            )
            for event in events["items"]:
                event_date = {}
                if check_attend(event) is True:
                    continue
                elif "start" not in event:
                    continue
                else:
                    event_date["start_time"] = event["start"]["dateTime"]
                    event_date["event_id"] = event["id"]
                    event_dates.append(event_date)

            page_token = events.get("nextPageToken")
            if not page_token:
                break
        return event_dates[:4]

    except Exception as e:
        abort(409, "Error in calling Google Calendar API to GET appointments")


def reformat(missing_values):
    reformatted = None
    if len(missing_values) == 1:
        reformatted = str(missing_values)
        reformatted = reformatted[2:-2]
    else:
        for i in missing_values:
            reformatted = str(reformatted) + ", " + str(i)
        reformatted = reformatted[6:]

    return reformatted


def check_availability(calendar_id, event_id, hos_id):
    service = get_service(hos_id)
    try:
        current_app.logger.info("Checking event availability...")
        event_to_check = (
            service.events().get(calendarId=calendar_id, eventId=event_id).execute()
        )
    except Exception as e:
        abort(409, "Error in calling Google Calendar API.")
    return not check_attend(event_to_check)


def cancel_my_turno(calendar_id, chosen_event_id, event_to_update, hos_id):
    service = get_service(hos_id)
    try:
        current_app.logger.info(
            "Attempting to cancel event info with Google Calendar API..."
        )
        service.events().update(
            calendarId=calendar_id, eventId=chosen_event_id, body=event_to_update
        ).execute()
        current_app.logger.info("Success! Event cancelled with Google Calendar API")
    except Exception as e:
        abort(409, "Could not cancel event with Google Calendar API")


def book_event(calendar_id, chosen_event_id, event_text, hos_id):
    service = get_service(hos_id)
    event_json = get_event(calendar_id, chosen_event_id, hos_id)
    event_text = event_text.replace("'", '"')
    event_text = json.loads(event_text)
    event_json["description"] = event_text["description"]
    event_json["summary"] = event_text["summary"]
    event_json["attendees"] = event_text["attendees"]
    event_to_update = event_json
    try:
        current_app.logger.info(
            "Attempting to update event info with Google Calendar API..."
        )
        service.events().update(
            calendarId=calendar_id, eventId=chosen_event_id, body=event_to_update
        ).execute()
        current_app.logger.info("Success! Event updated with Google Calendar API")
    except Exception as e:
        abort(409, "Could not update event information with Google Calendar API")


def find_my_appointments(email, hos_id):
    """
    Returns all appointments associated with an email.
    To be used for cancel_form or consult_appointments action.
    """
    my_appointments = []
    service = get_service(hos_id)
    calendars_all = []
    page_token = None
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        for calendar_list_entry in calendar_list["items"]:
            calendars_all.append(calendar_list_entry["id"])
        page_token = calendar_list.get("nextPageToken")
        if not page_token:
            break
    if "asistocovid@gmail.com" in calendars_all:
        calendars_all.remove("asistocovid@gmail.com")
    if "demoasistente2020@gmail.com" in calendars_all:
        calendars_all.remove("demoasistente2020@gmail.com")
    calendars_all.remove("es.ar#holiday@group.v.calendar.google.com")
    calendars_all.remove("addressbook#contacts@group.v.calendar.google.com")
    date_today = datetime.now(timezone.utc).astimezone()
    timemin = date_today.isoformat()
    for cal_id in calendars_all:
        events = (
            service.events()
            .list(
                calendarId=cal_id, timeMin=timemin, timeZone="America/Argentina/Cordoba"
            )
            .execute()
        )
        for event in events["items"]:
            appt_data = {}
            if "attendees" in event and event["attendees"][0]["email"] == email:
                appt_data["start_time"] = event["start"]["dateTime"]
                appt_data["calendar_id"] = cal_id
                appt_data["event_id"] = event["id"]
                my_appointments.append(appt_data)
    return my_appointments


def cancel_appointment(calendar_id, chosen_event_id, hos_id, event_text):
    """
    Cancels appointment by rewriting description, summary
    and attendees of Google Calendar event.

    Event summary must be a dictionary:
    event_text = {"summary": "turno abierto >doctor< + >headquarters<"}
    """
    service = get_service(hos_id)
    # retrieve event
    try:
        current_app.logger.info(
            "Attempting to retrieve event information from Google Calendar API..."
        )
        cancel_event = (
            service.events()
            .get(calendarId=calendar_id, eventId=chosen_event_id)
            .execute()
        )
    except Exception as e:
        current_app.logger.debug(
            f"Cancel appointment in Google Calender API failed with exception: {e}"
        )
        abort(
            409,
            "Could not cancel appointment. Check the parameters used to call Google Calendar API",
        )
    # erase description
    cancel_event["description"] = ""
    # reset summary
    cancel_event["summary"] = event_text
    # delete attendee
    key_del = "attendees"
    try:
        cancel_event.pop(key_del)
    except KeyError:
        current_app.logger.debug(f"Key {key_del} not in dictionary")
    event_to_update = cancel_event
    # this "cancels" the appointment
    cancel_my_turno(calendar_id, chosen_event_id, event_to_update, hos_id)
