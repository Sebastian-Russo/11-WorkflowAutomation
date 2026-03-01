"""
Think of this like a job posting board.
Claude reads these descriptions and decides which jobs to assign itself.
The descriptions don't DO anything — they just tell Claude what's available
and what information is needed to use each capability.

This is the bridge between natural language and API calls.
Claude reads "get_recent_emails" and understands when and how to use it.
"""


# ── Gmail tools ───────────────────────────────────────────────
GET_RECENT_EMAILS = {
    "name": "get_recent_emails",
    "description": """Fetch recent emails from Gmail. Use this when the user wants to:
- Read their emails
- Find emails from a specific person
- Search for emails about a topic
- Check unread messages
Supports Gmail search syntax e.g. 'from:john@example.com', 'is:unread', 'subject:meeting'""",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type":        "string",
                "description": "Gmail search query. Empty string returns most recent emails."
            },
            "max_results": {
                "type":        "integer",
                "description": "Number of emails to fetch. Default 10, max 20.",
                "default":     10
            }
        },
        "required": []
    }
}

SEND_EMAIL = {
    "name": "send_email",
    "description": """Send an email from the user's Gmail account. Use this when the user wants to:
- Send a new email
- Reply to someone (compose a new message to them)
- Follow up with a contact
Always confirm the recipient, subject, and key content before sending.""",
    "input_schema": {
        "type": "object",
        "properties": {
            "to": {
                "type":        "string",
                "description": "Recipient email address"
            },
            "subject": {
                "type":        "string",
                "description": "Email subject line"
            },
            "body": {
                "type":        "string",
                "description": "Full email body text"
            }
        },
        "required": ["to", "subject", "body"]
    }
}

# ── Calendar tools ────────────────────────────────────────────
GET_UPCOMING_EVENTS = {
    "name": "get_upcoming_events",
    "description": """Fetch upcoming events from Google Calendar. Use this when the user wants to:
- Check their schedule
- See what's coming up today, tomorrow, this week
- Find out if they're free at a certain time
- Review upcoming meetings or appointments""",
    "input_schema": {
        "type": "object",
        "properties": {
            "days_ahead": {
                "type":        "integer",
                "description": "How many days ahead to look. Default 7.",
                "default":     7
            },
            "max_results": {
                "type":        "integer",
                "description": "Maximum number of events to return. Default 20.",
                "default":     20
            }
        },
        "required": []
    }
}

CREATE_EVENT = {
    "name": "create_event",
    "description": """Create a new event in Google Calendar. Use this when the user wants to:
- Schedule a meeting
- Block off time
- Add an appointment
Convert natural language times like 'Friday at 2pm' to ISO format datetime strings.""",
    "input_schema": {
        "type": "object",
        "properties": {
            "title": {
                "type":        "string",
                "description": "Event title"
            },
            "start_time": {
                "type":        "string",
                "description": "Start time in ISO format e.g. '2026-03-01T14:00:00'"
            },
            "end_time": {
                "type":        "string",
                "description": "End time in ISO format e.g. '2026-03-01T15:00:00'"
            },
            "description": {
                "type":        "string",
                "description": "Optional event description or notes"
            }
        },
        "required": ["title", "start_time", "end_time"]
    }
}

# ── All tools as a list — passed directly to the Anthropic API ─
ALL_TOOLS = [
    GET_RECENT_EMAILS,
    SEND_EMAIL,
    GET_UPCOMING_EVENTS,
    CREATE_EVENT
]
