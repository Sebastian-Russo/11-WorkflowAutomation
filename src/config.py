import os
from dotenv import load_dotenv

load_dotenv()

# Anthropic — same as every other project
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Using one model for everything — unlike previous projects we don't split
# fast/smart because every step here involves real reasoning about what
# tools to call and what data to act on. Haiku would make mistakes.
CLAUDE_MODEL = "claude-sonnet-4-6"

# ── Google OAuth — NEW concept ────────────────────────────────
# Think of these like two different ID cards:
#
# CREDENTIALS_FILE = your app's ID card — proves to Google who your app is.
#   You downloaded this from Google Cloud Console. It never changes.
#
# TOKEN_FILE = your personal access pass — proves YOU authorized the app.
#   This doesn't exist yet. It gets created automatically the first time
#   you run the app and click "Allow" in the browser. After that it sits
#   here and refreshes itself silently every hour when it expires.
#
# You only do the "click Allow" dance once. Every run after that is silent.
CREDENTIALS_FILE = "credentials/google_credentials.json"
TOKEN_FILE       = "credentials/google_token.json"

# ── OAuth Scopes — what permissions we're requesting ──────────
# Scopes are like a specific list of keys on a keyring.
# Instead of giving your app master access to your Google account,
# you say exactly: "this app can read Gmail, send Gmail, read Calendar,
# and create Calendar events — nothing else."
#
# These must match EXACTLY what you added in the OAuth consent screen.
# If they don't match, Google will reject the auth flow.
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",   # read emails
    "https://www.googleapis.com/auth/gmail.send",        # send emails
    "https://www.googleapis.com/auth/gmail.compose",     # draft emails
    "https://www.googleapis.com/auth/calendar.readonly", # read calendar
    "https://www.googleapis.com/auth/calendar.events"    # create/edit events
]

# How many emails to fetch at once — keeps responses fast and tokens low
EMAIL_FETCH_LIMIT = 10
