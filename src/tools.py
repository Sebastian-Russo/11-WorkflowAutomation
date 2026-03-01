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

# ── Tasks tools ───────────────────────────────────────────────
GET_TASKS = {
    "name": "get_tasks",
    "description": """Fetch tasks from the user's Google Tasks. Use this when the user wants to:
- See their to-do list
- Check what tasks they have pending
- Review tasks due soon
- Look at a specific task list""",
    "input_schema": {
        "type": "object",
        "properties": {
            "tasklist_id": {
                "type":        "string",
                "description": "Task list ID. Use '@default' for the primary list.",
                "default":     "@default"
            },
            "show_completed": {
                "type":        "boolean",
                "description": "Whether to include completed tasks. Default false.",
                "default":     False
            }
        },
        "required": []
    }
}

CREATE_TASK = {
    "name": "create_task",
    "description": """Create a new task in Google Tasks. Use this when the user wants to:
- Add something to their to-do list
- Create a reminder
- Log something they need to do later""",
    "input_schema": {
        "type": "object",
        "properties": {
            "title": {
                "type":        "string",
                "description": "Task title"
            },
            "notes": {
                "type":        "string",
                "description": "Optional notes or details about the task"
            },
            "due": {
                "type":        "string",
                "description": "Optional due date in RFC 3339 format e.g. '2026-03-01T00:00:00.000Z'"
            },
            "tasklist_id": {
                "type":        "string",
                "description": "Task list ID. Use '@default' for the primary list.",
                "default":     "@default"
            }
        },
        "required": ["title"]
    }
}

COMPLETE_TASK = {
    "name": "complete_task",
    "description": """Mark a task as completed in Google Tasks. Use this when the user wants to:
- Check off a task
- Mark something as done
- Complete an item on their to-do list
First call get_tasks to find the task_id, then call this.""",
    "input_schema": {
        "type": "object",
        "properties": {
            "task_id": {
                "type":        "string",
                "description": "The task ID to mark as complete. Get this from get_tasks."
            },
            "tasklist_id": {
                "type":        "string",
                "description": "Task list ID. Use '@default' for the primary list.",
                "default":     "@default"
            }
        },
        "required": ["task_id"]
    }
}

# ── Drive tools ───────────────────────────────────────────────
SEARCH_FILES = {
    "name": "search_files",
    "description": """Search for files in Google Drive. Use this when the user wants to:
- Find a specific document, spreadsheet, or file
- Look for files by name or topic
- Browse recent files
- Locate a presentation or PDF
Supports Drive query syntax for precise searches.""",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type":        "string",
                "description": "Drive search query e.g. \"name contains 'budget'\" or \"name contains 'meeting notes'\""
            },
            "max_results": {
                "type":        "integer",
                "description": "Maximum number of files to return. Default 10.",
                "default":     10
            }
        },
        "required": ["query"]
    }
}

GET_FILE_CONTENT = {
    "name": "get_file_content",
    "description": """Read the text content of a Google Doc or text file. Use this when the user wants to:
- Read or summarize a specific document
- Extract information from a file
- Review the contents of a doc
First use search_files to find the file_id, then call this.""",
    "input_schema": {
        "type": "object",
        "properties": {
            "file_id": {
                "type":        "string",
                "description": "The file ID from search_files results"
            }
        },
        "required": ["file_id"]
    }
}

# ── Sheets tools ──────────────────────────────────────────────
GET_SHEET_VALUES = {
    "name": "get_sheet_values",
    "description": """Read data from a Google Sheets spreadsheet. Use this when the user wants to:
- Read data from a spreadsheet
- Check values in a specific sheet
- Review a table of data
- Look up information stored in a sheet
The spreadsheet_id is the long string in the Google Sheets URL.""",
    "input_schema": {
        "type": "object",
        "properties": {
            "spreadsheet_id": {
                "type":        "string",
                "description": "The spreadsheet ID from the URL e.g. '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms'"
            },
            "range_name": {
                "type":        "string",
                "description": "A1 notation range e.g. 'Sheet1' or 'Sheet1!A1:D10'. Defaults to Sheet1.",
                "default":     "Sheet1"
            }
        },
        "required": ["spreadsheet_id"]
    }
}

APPEND_ROW = {
    "name": "append_row",
    "description": """Append a new row to a Google Sheets spreadsheet. Use this when the user wants to:
- Add a new entry to a spreadsheet
- Log data to a sheet
- Add a row to a table
- Record something in a spreadsheet""",
    "input_schema": {
        "type": "object",
        "properties": {
            "spreadsheet_id": {
                "type":        "string",
                "description": "The spreadsheet ID from the URL"
            },
            "values": {
                "type":        "array",
                "items":       {"type": "string"},
                "description": "List of values for the new row in column order e.g. ['2026-03-01', 'Groceries', '45.00']"
            },
            "range_name": {
                "type":        "string",
                "description": "Sheet name to append to. Defaults to Sheet1.",
                "default":     "Sheet1"
            }
        },
        "required": ["spreadsheet_id", "values"]
    }
}

UPDATE_CELL = {
    "name": "update_cell",
    "description": """Update a single cell in a Google Sheets spreadsheet. Use this when the user wants to:
- Change a specific value in a spreadsheet
- Update a cell
- Correct an entry in a sheet""",
    "input_schema": {
        "type": "object",
        "properties": {
            "spreadsheet_id": {
                "type":        "string",
                "description": "The spreadsheet ID from the URL"
            },
            "cell": {
                "type":        "string",
                "description": "Cell in A1 notation e.g. 'Sheet1!B5'"
            },
            "value": {
                "type":        "string",
                "description": "New value for the cell"
            }
        },
        "required": ["spreadsheet_id", "cell", "value"]
    }
}

# ── Docs tools ────────────────────────────────────────────────
GET_DOCUMENT = {
    "name": "get_document",
    "description": """Read the content of a Google Doc. Use this when the user wants to:
- Read or summarize a specific document
- Extract information from a doc
- Review the contents of a Google Doc
The document_id is the long string in the Google Docs URL.""",
    "input_schema": {
        "type": "object",
        "properties": {
            "document_id": {
                "type":        "string",
                "description": "The document ID from the URL"
            }
        },
        "required": ["document_id"]
    }
}

CREATE_DOCUMENT = {
    "name": "create_document",
    "description": """Create a new Google Doc with content. Use this when the user wants to:
- Save generated text as a document
- Create meeting notes
- Draft and store a document permanently
Returns a link to the newly created document.""",
    "input_schema": {
        "type": "object",
        "properties": {
            "title":   {"type": "string", "description": "Document title"},
            "content": {"type": "string", "description": "Full text content"}
        },
        "required": ["title", "content"]
    }
}

APPEND_TO_DOCUMENT = {
    "name": "append_to_document",
    "description": """Append text to the end of an existing Google Doc. Use this when the user wants to:
- Add content to an existing document
- Update a running log or notes doc
- Add a new section without replacing existing content""",
    "input_schema": {
        "type": "object",
        "properties": {
            "document_id": {"type": "string", "description": "The document ID from the URL"},
            "content":     {"type": "string", "description": "Text to append"}
        },
        "required": ["document_id", "content"]
    }
}

LIST_HEADINGS = {
    "name": "list_headings",
    "description": """List all headings in a Google Doc to understand its structure. Use this when the user wants to:
- Get an overview of a long document
- Find out what sections a doc contains
- Navigate a document before reading it
- Understand the structure of a report or notes doc""",
    "input_schema": {
        "type": "object",
        "properties": {
            "document_id": {"type": "string", "description": "The document ID from the URL"}
        },
        "required": ["document_id"]
    }
}

SEARCH_IN_DOCUMENT = {
    "name": "search_in_document",
    "description": """Search for a specific term within a Google Doc. Use this when the user wants to:
- Find where a topic is mentioned in a document
- Locate a specific paragraph or section
- Check if something appears in a doc""",
    "input_schema": {
        "type": "object",
        "properties": {
            "document_id": {"type": "string", "description": "The document ID from the URL"},
            "search_term": {"type": "string", "description": "Term to search for"}
        },
        "required": ["document_id", "search_term"]
    }
}

FORMAT_TEXT = {
    "name": "format_text",
    "description": """Apply formatting to text in a Google Doc. Use this when the user wants to:
- Bold or italicize specific text
- Apply a heading style to a section
- Format a title or subtitle""",
    "input_schema": {
        "type": "object",
        "properties": {
            "document_id":   {"type": "string",  "description": "The document ID from the URL"},
            "text_to_find":  {"type": "string",  "description": "The exact text to format"},
            "bold":          {"type": "boolean", "description": "Apply bold formatting", "default": False},
            "italic":        {"type": "boolean", "description": "Apply italic formatting", "default": False},
            "heading_level": {"type": "integer", "description": "Heading level 1-6. Overrides bold/italic."}
        },
        "required": ["document_id", "text_to_find"]
    }
}

DELETE_CONTENT = {
    "name": "delete_content",
    "description": """Delete specific text from a Google Doc. Use this when the user wants to:
- Remove a section from a document
- Delete a paragraph or sentence
- Clean up a document
WARNING: This is permanent and cannot be undone via API.""",
    "input_schema": {
        "type": "object",
        "properties": {
            "document_id":     {"type": "string", "description": "The document ID from the URL"},
            "text_to_delete":  {"type": "string", "description": "The exact text to delete"}
        },
        "required": ["document_id", "text_to_delete"]
    }
}

# ── All tools as a list — passed directly to the Anthropic API ─
ALL_TOOLS = [
    GET_RECENT_EMAILS,
    SEND_EMAIL,
    GET_UPCOMING_EVENTS,
    CREATE_EVENT,
    GET_TASKS,
    CREATE_TASK,
    COMPLETE_TASK,
    SEARCH_FILES,
    GET_FILE_CONTENT,
    GET_SHEET_VALUES,
    APPEND_ROW,
    UPDATE_CELL,
    GET_DOCUMENT,
    CREATE_DOCUMENT,
    APPEND_TO_DOCUMENT,
    LIST_HEADINGS,
    SEARCH_IN_DOCUMENT,
    FORMAT_TEXT,
    DELETE_CONTENT
]
