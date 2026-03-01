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
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os

from src.config import CREDENTIALS_FILE, TOKEN_FILE, SCOPES, EMAIL_FETCH_LIMIT


def get_gmail_service():
    """
    Authenticate with Google and return a Gmail API service object.

    First run: opens a browser window asking you to click Allow.
    Every run after: silently loads the saved token and refreshes if expired.

    Think of this like a bouncer checking your ID — first time you
    need to show your passport, after that your membership card works.
    """
    creds = None

    # Load existing token if it exists
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # If no valid token, run the OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Token expired — refresh it silently without user interaction
            creds.refresh(Request())
        else:
            # No token at all — open browser for user to click Allow
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save token for next run
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


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
