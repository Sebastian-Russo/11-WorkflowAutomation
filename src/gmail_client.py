"""
Think of this like a personal mail assistant who has a key to your mailbox.
They can read your letters, summarize them, and send new ones on your behalf.
But they can only do exactly what you gave them a key for — nothing else.

This file handles all Gmail API communication. Claude never touches
Gmail directly — it asks this file to do things, and this file
translates those requests into Gmail API calls.
"""

import base64
import email
from email.mime.text import MIMEText
from googleapiclient.discovery import build, Resource
from src.auth import get_credentials
import os

from src.config import EMAIL_FETCH_LIMIT


def get_gmail_service() -> Resource:
    return build("gmail", "v1", credentials=get_credentials())


def get_recent_emails(query: str = "", max_results: int = EMAIL_FETCH_LIMIT) -> list[dict]:
    """
    Fetch recent emails matching an optional Gmail search query.

    Gmail query syntax works here — same as the Gmail search bar:
      "from:john@example.com"
      "subject:meeting"
      "is:unread"
      "after:2024/01/01"
    """
    service = get_gmail_service()

    # Step 1: get list of message IDs matching the query
    # type: ignore[attr-defined] - Google API dynamically generates methods
    result   = service.users().messages().list(
        userId      = "me",
        q           = query,
        maxResults  = max_results
    ).execute()

    messages = result.get("messages", [])
    if not messages:
        return []

    # Step 2: fetch full content for each message ID
    emails = []
    for msg in messages:
        try:
            # type: ignore[attr-defined] - Google API dynamically generates methods
            full_msg = service.users().messages().get(
                userId  = "me",
                id      = msg["id"],
                format  = "full"
            ).execute()
            emails.append(_parse_email(full_msg))
        except Exception as e:
            print(f"[Gmail] Error fetching message {msg['id']}: {e}")
            continue

    return emails


def send_email(to: str, subject: str, body: str) -> dict:
    """
    Send an email from your Gmail account.

    Returns a result dict with success status and message ID.
    """
    service = get_gmail_service()

    # Gmail API requires emails to be base64-encoded RFC 2822 format
    # MIMEText handles that encoding for us
    message     = MIMEText(body)
    message["to"]      = to
    message["subject"] = subject

    encoded = base64.urlsafe_b64encode(message.as_bytes()).decode()

    try:
        # type: ignore[attr-defined] - Google API dynamically generates methods
        sent = service.users().messages().send(
            userId = "me",
            body   = {"raw": encoded}
        ).execute()
        return {"success": True, "message_id": sent["id"]}
    except Exception as e:
        return {"success": False, "error": str(e)}


def _parse_email(msg: dict) -> dict:
    """
    Extract readable fields from Gmail's raw message format.

    Gmail returns a deeply nested structure — this flattens it into
    something Claude can easily read and reason about.
    """
    headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}

    # Extract plain text body — walk the MIME parts to find it
    body = ""
    payload = msg["payload"]

    if "parts" in payload:
        for part in payload["parts"]:
            if part["mimeType"] == "text/plain" and "data" in part.get("body", {}):
                body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="replace")
                break
    elif "body" in payload and "data" in payload["body"]:
        body = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")

    return {
        "id":      msg["id"],
        "from":    headers.get("From", ""),
        "to":      headers.get("To", ""),
        "subject": headers.get("Subject", ""),
        "date":    headers.get("Date", ""),
        "body":    body[:2000]   # cap at 2000 chars to keep token usage reasonable
    }
