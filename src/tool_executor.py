"""
Think of this like a dispatcher at a call center.
Claude says "I need task X done with these parameters."
The dispatcher looks up who handles task X and routes the call.

This file sits between Claude's tool requests and the actual
API clients. Claude never calls Gmail or Calendar directly —
it always goes through here.
"""

from src.gmail_client    import get_recent_emails, send_email
from src.calendar_client import get_upcoming_events, create_event
from src.tasks_client import get_tasks, create_task, complete_task
from src.drive_client import search_files, get_file_content

def execute_tool(tool_name: str, tool_input: dict) -> dict:
    """
    Route a tool call from Claude to the correct API client function.

    tool_name:  matches the "name" field in tools.py exactly
    tool_input: the arguments Claude decided to pass

    Returns a dict that gets fed back to Claude as the tool result.
    """
    print(f"[ToolExecutor] Executing: {tool_name} with {tool_input}")

    if tool_name == "get_recent_emails":
        query       = tool_input.get("query", "")
        max_results = tool_input.get("max_results", 10)
        emails      = get_recent_emails(query=query, max_results=max_results)

        if not emails:
            return {"result": "No emails found matching that query."}

        # Format emails into readable text for Claude to reason about
        formatted = []
        for i, e in enumerate(emails, 1):
            formatted.append(
                f"Email {i}:\n"
                f"  From:    {e['from']}\n"
                f"  Subject: {e['subject']}\n"
                f"  Date:    {e['date']}\n"
                f"  Body:    {e['body'][:500]}..."
            )
        return {"result": "\n\n".join(formatted), "count": len(emails)}

    elif tool_name == "send_email":
        to      = tool_input.get("to", "")
        subject = tool_input.get("subject", "")
        body    = tool_input.get("body", "")

        if not to or not subject or not body:
            return {"error": "Missing required fields: to, subject, or body"}

        result = send_email(to=to, subject=subject, body=body)
        return result

    elif tool_name == "get_upcoming_events":
        days_ahead  = tool_input.get("days_ahead", 7)
        max_results = tool_input.get("max_results", 20)
        events      = get_upcoming_events(days_ahead=days_ahead, max_results=max_results)

        if not events:
            return {"result": "No upcoming events found."}

        # Format events into readable text for Claude to reason about
        formatted = []
        for i, e in enumerate(events, 1):
            attendees = ", ".join(e["attendees"]) if e["attendees"] else "none"
            formatted.append(
                f"Event {i}:\n"
                f"  Title:     {e['title']}\n"
                f"  Start:     {e['start']}\n"
                f"  End:       {e['end']}\n"
                f"  Location:  {e['location'] or 'none'}\n"
                f"  Attendees: {attendees}"
            )
        return {"result": "\n\n".join(formatted), "count": len(events)}

    elif tool_name == "create_event":
        title       = tool_input.get("title", "")
        start_time  = tool_input.get("start_time", "")
        end_time    = tool_input.get("end_time", "")
        description = tool_input.get("description", "")

        if not title or not start_time or not end_time:
            return {"error": "Missing required fields: title, start_time, or end_time"}

        result = create_event(
            title       = title,
            start_time  = start_time,
            end_time    = end_time,
            description = description
        )
        return result

    elif tool_name == "get_tasks":
        tasklist_id     = tool_input.get("tasklist_id", "@default")
        show_completed  = tool_input.get("show_completed", False)
        tasks           = get_tasks(tasklist_id=tasklist_id, show_completed=show_completed)

        if not tasks:
            return {"result": "No tasks found."}

        formatted = []
        for i, t in enumerate(tasks, 1):
            due  = f"  Due: {t['due']}\n" if t["due"] else ""
            note = f"  Notes: {t['notes']}\n" if t["notes"] else ""
            formatted.append(
                f"Task {i} [id: {t['id']}]:\n"
                f"  Title:  {t['title']}\n"
                f"  Status: {t['status']}\n"
                f"{due}{note}"
            )
        return {"result": "\n\n".join(formatted), "count": len(tasks)}

    elif tool_name == "create_task":
        title       = tool_input.get("title", "")
        notes       = tool_input.get("notes", "")
        due         = tool_input.get("due", "")
        tasklist_id = tool_input.get("tasklist_id", "@default")

        if not title:
            return {"error": "Task title is required"}

        return create_task(title=title, notes=notes, due=due, tasklist_id=tasklist_id)

    elif tool_name == "complete_task":
        task_id     = tool_input.get("task_id", "")
        tasklist_id = tool_input.get("tasklist_id", "@default")

        if not task_id:
            return {"error": "task_id is required"}

        return complete_task(task_id=task_id, tasklist_id=tasklist_id)

    elif tool_name == "search_files":
        query       = tool_input.get("query", "")
        max_results = tool_input.get("max_results", 10)

        if not query:
            return {"error": "Search query is required"}

        files = search_files(query=query, max_results=max_results)

        if not files:
            return {"result": "No files found matching that query."}

        formatted = []
        for i, f in enumerate(files, 1):
            formatted.append(
                f"File {i} [id: {f['id']}]:\n"
                f"  Name:     {f['name']}\n"
                f"  Type:     {f['type']}\n"
                f"  Modified: {f['modified']}\n"
                f"  Link:     {f['link']}"
            )
        return {"result": "\n\n".join(formatted), "count": len(files)}

    elif tool_name == "get_file_content":
        file_id = tool_input.get("file_id", "")

        if not file_id:
            return {"error": "file_id is required"}

        return get_file_content(file_id=file_id)

    else:
        return {"error": f"Unknown tool: {tool_name}"}
