"""
Think of this like a personal secretary who manages your calendar.
They can tell you what's coming up, block off time, and create
new appointments — but only because you explicitly gave them access.

Same OAuth pattern as gmail_client.py — same key, same token,
different API endpoint.
"""

from datetime import datetime, timedelta
from googleapiclient.discovery import build, Resource

from src.auth import get_credentials

def get_calendar_service() -> Resource:
    return build("calendar", "v3", credentials=get_credentials())

def get_upcoming_events(days_ahead: int = 7, max_results: int = 20) -> list[dict]:
    """
    Fetch upcoming calendar events within the next N days.

    Returns events in chronological order with clean readable fields.
    """
    service = get_calendar_service()

    # Google Calendar requires RFC 3339 timestamps — include timezone
    now      = datetime.utcnow().isoformat() + "Z"
    end_time = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat() + "Z"

    # type: ignore[attr-defined] - Google API dynamically generates methods
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
        # type: ignore[attr-defined] - Google API dynamically generates methods
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
