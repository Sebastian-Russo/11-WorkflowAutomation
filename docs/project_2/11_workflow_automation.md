# Workflow Automation

Connecting Claude to real services via their APIs.

This is the most practically useful project on the list. You've already built everything that makes it work conceptually — tools from the agent project, orchestration from the research agent. The new skill here is real API integrations.

You have Gmail and Google Calendar connected in your Claude account. So let's build a personal assistant that can:

- Read your emails
- Draft and send responses
- Check your calendar
- Create events
- Do multi-step tasks combining both — "check my calendar tomorrow, draft an email to my team with the schedule"


## Option 1: Gmail + Google Calendar APIs directly

You write Python code that calls Google's REST APIs using their official Python libraries. Your code owns the entire integration.

**How it works:**

User request
    ↓
Claude decides what to do
    ↓
Your code calls Gmail API / Calendar API
    ↓
Results fed back to Claude
    ↓
Claude responds

**Setup required:**

- Create a Google Cloud project
- Enable Gmail and Calendar APIs
- Create OAuth 2.0 credentials
- Download a credentials JSON file
- Run an auth flow to get a token
- About 30-45 minutes of setup before writing any code

**Pros:**

- You own everything — full control over what gets read, sent, stored
- Works in any environment, any app, any server
- Production-ready — this is how real companies build Gmail integrations
- Teaches you OAuth, which is how almost every real API integration works
No dependency on Claude's infrastructure

**Cons:**

- More setup friction upfront
- You handle token refresh, error handling, pagination yourself
- More code to write


## Option 2: Claude MCP connectors

MCP (Model Context Protocol) is Anthropic's system for giving Claude direct access to external services. You've already connected Gmail and Google Calendar in your Claude.ai account. Instead of writing API integration code, you pass those MCP servers into the Anthropic API call and Claude uses them natively.

**How it works:**

User request
    ↓
Claude decides what to do
    ↓
Claude calls Gmail/Calendar MCP tool internally
    ↓
Claude responds with results already incorporated

**Setup required:**

- Already done — you connected them in Claude.ai
- Just pass the MCP server URLs in the API call
- About 5 minutes

**Pros:**

- Almost no setup — works immediately
- Less code to write
- Claude handles the tool execution internally
- Great for prototyping fast

**Cons:**

- Dependent on Anthropic's MCP infrastructure
- Less control — you can't customize what gets fetched or how
- Not portable — can't deploy this to your own server for other users
- MCP is still relatively new, less battle-tested than direct APIs
- Harder to debug when something goes wrong — the tool execution is a black box


## The honest recommendation

Learn both. But in a specific order.
Build this project with MCP first — you'll have a working assistant in one session, and you'll understand the tool-use pattern deeply from the research agent project. It lets you focus on the orchestration logic rather than OAuth plumbing.
Then as a follow-up, swap the MCP layer for direct Gmail/Calendar API calls. You'll appreciate the contrast — same assistant, completely different integration layer. That's when OAuth and direct API calls make the most sense to learn, because you already know what you're building toward.
The direct API approach is what you'd use in production. MCP is what you'd use to prototype fast or build personal tools.
Which way do you want to go?I want to learn both, but start with the api first9:17 PMGood call — learning the harder way first means MCP will feel trivial afterwards.
Let me lay out what's new before we write anything.

## The New Concept: OAuth 2.0

Every project so far used an API key — a static string in your .env file. Google doesn't work that way for personal data like email and calendar. They use OAuth 2.0.

OAuth is a permission system. Instead of giving your app a password, you tell Google "this app wants to read my Gmail" and Google asks you directly: "do you allow this?" You click yes, Google gives your app a temporary token, and that token is what your code uses to make API calls.

**The flow looks like this:**
Your app → Google: "I want access to this user's Gmail"
Google → User:    "Do you allow this app to read your email?"
User → Google:    "Yes"
Google → Your app: "Here's a token, use this for API calls"
Your app → Gmail API: requests using that token
The token expires after an hour. Google also gives you a refresh token that lets you get a new access token automatically without asking the user again.
You do this dance once. After that your app runs silently.

## What You're Building

A personal assistant Flask app where you type natural language requests and Claude figures out which Gmail and Calendar tools to call:

"What emails did I get today from anyone about meetings?"
"Draft a reply to the last email from John saying I'll be there at 3pm"
"What's on my calendar tomorrow?"
"Create an event Friday at 2pm called Team Sync"
"Check my calendar next week and send Sarah an email with my availability"

That last one is the interesting case — Claude chains two tools together autonomously.

## Project Structure

11-WorkflowAutomation/
├── src/
│   ├── config.py
│   ├── gmail_client.py       ← Gmail API wrapper
│   ├── calendar_client.py    ← Google Calendar API wrapper
│   ├── tools.py              ← tool definitions Claude can call
│   ├── tool_executor.py      ← executes tool calls Claude requests
│   ├── assistant.py          ← orchestrates the full conversation loop
│   └── __init__.py
├── static/
│   └── index.html
├── credentials/              ← Google OAuth credentials live here
├── app.py
├── requirements.txt
└── .gitignore

## Setup You Need To Do First

Before we write any code you need Google credentials. This takes about 20 minutes and only happens once.

**Step 1:** Go to console.cloud.google.com
**Step 2:** Create a new project — call it anything like "WorkflowAssistant"
**Step 3:** Enable two APIs:

Search "Gmail API" → Enable
Search "Google Calendar API" → Enable

**Step 4:** Go to "APIs & Services" → "OAuth consent screen"

Choose "External"
Fill in app name and your email
Add scopes: gmail.readonly, gmail.send, calendar.readonly, calendar.events
Add your email as a test user

**Step 5:** Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"

Application type: Desktop app
Download the JSON file
Save it as credentials/google_credentials.json in your project
