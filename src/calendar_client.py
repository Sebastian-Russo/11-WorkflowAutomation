"""
Think of this like a personal secretary who manages your calendar.
They can tell you what's coming up, block off time, and create
new appointments — but only because you explicitly gave them access.

Same OAuth pattern as gmail_client.py — same key, same token,
different API endpoint.
"""

from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os

from src.config import CREDENTIALS_FILE, TOKEN_FILE, SCOPES


def get_calendar_service():
    """
    Authenticate and return a Calendar API service object.

    Reuses the same token file as Gmail — one OAuth flow gives
    access to both services because we requested both scopes upfront.
    This is why the SCOPES list in config.py includes both Gmail and Calendar.
    """
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow  = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())

    # Only difference from gmail_client — "calendar" instead of "gmail"
    return build("calendar", "v3", credentials=creds)


def get_upcoming_events(days_ahead: int = 7, max_results: int = 20) -> list[dict]:
    """
    Fetch upcoming calendar events within the next N days.

    Returns events in chronological order with clean readable fields.
    """
    service = get_calendar_service()

    # Google Calendar requires RFC 3339 timestamps — include timezone
    now      = datetime.utcnow().isoformat() + "Z"
    end_time = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat() + "Z"

    result = service.events().list(
        calendarId   = "primary",
        timeMin      = now,
        timeMax      = end_time,
        maxResults   = max_results,
        singleEvents = True,          # expand recurring events into individual instances
        orderBy      = "startTime"    # chronological order
    ).execute()

    events = result.get("items", [])
    return [_parse_event(e) for e in events]


def create_event(title: str, start_time: str, end_time: str, description: str = "") -> dict:
    """
    Create a new calendar event.

    start_time and end_time should be ISO format strings.
    e.g. "2026-03-01T14:00:00" for March 1st at 2pm.

    Claude will generate these from natural language like
    "Friday at 2pm" — that's Claude's job, not ours.
    """
    service = get_calendar_service()

    event = {
        "summary":     title,
        "description": description,
        "start": {
            "dateTime": start_time,
            "timeZone": "America/New_York"   # adjust to your timezone
        },
        "end": {
            "dateTime": end_time,
            "timeZone": "America/New_York"
        }
    }

    try:
        created = service.events().insert(
            calendarId = "primary",
            body       = event
        ).execute()
        return {
            "success":  True,
            "event_id": created["id"],
            "title":    title,
            "start":    start_time,
            "link":     created.get("htmlLink", "")
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def _parse_event(event: dict) -> dict:
    """
    Flatten Google Calendar's nested event format into clean readable fields.
    Handles both timed events and all-day events (which have "date" not "dateTime").
    """
    start = event.get("start", {})
    end   = event.get("end", {})

    return {
        "id":          event.get("id", ""),
        "title":       event.get("summary", "No title"),
        "start":       start.get("dateTime", start.get("date", "")),
        "end":         end.get("dateTime",   end.get("date", "")),
        "description": event.get("description", ""),
        "location":    event.get("location", ""),
        "attendees":   [a["email"] for a in event.get("attendees", [])]
    }
