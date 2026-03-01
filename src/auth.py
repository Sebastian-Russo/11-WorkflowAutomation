"""
Think of this like a front desk receptionist who checks everyone's ID.
Instead of every department having their own security check,
there's one central auth point that everyone goes through.

Every API client (Gmail, Calendar, Tasks, Drive, Sheets, Docs)
imports get_credentials() from here instead of each managing
their own OAuth flow.
"""

import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from src.config import CREDENTIALS_FILE, TOKEN_FILE, SCOPES


def get_credentials() -> Credentials:
    """
    Load or refresh Google OAuth credentials.

    First run: opens browser for user to click Allow.
    Every run after: loads saved token, refreshes silently if expired.
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

    return creds
