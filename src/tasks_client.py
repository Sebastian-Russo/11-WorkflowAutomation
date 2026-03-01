"""
Think of this like a to-do list manager who can read your lists,
add new items, and mark things as done — all from a single request.

Same pattern as gmail_client and calendar_client — import credentials
from auth.py, build the service, call the API, return clean dicts.
"""

from googleapiclient.discovery import build, Resource
from src.auth   import get_credentials


def get_tasks_service() -> Resource:
    return build("tasks", "v1", credentials=get_credentials())


def get_task_lists() -> list[dict]:
    """Fetch all task lists in the user's account."""
    service = get_tasks_service()
    # type: ignore[attr-defined] - Google API dynamically generates methods
    result  = service.tasklists().list().execute()
    lists   = result.get("items", [])

    return [
        {"id": l["id"], "title": l["title"]}
        for l in lists
    ]


def get_tasks(tasklist_id: str = "@default", show_completed: bool = False) -> list[dict]:
    """
    Fetch tasks from a specific list.
    '@default' is Google's shorthand for the user's primary task list.
    """
    service = get_tasks_service()
    # type: ignore[attr-defined] - Google API dynamically generates methods
    result  = service.tasks().list(
        tasklist       = tasklist_id,
        showCompleted  = show_completed,
        showHidden     = False
    ).execute()

    tasks = result.get("items", [])

    return [
        {
            "id":       t["id"],
            "title":    t.get("title", ""),
            "status":   t.get("status", ""),   # "needsAction" or "completed"
            "due":      t.get("due", ""),
            "notes":    t.get("notes", "")
        }
        for t in tasks
    ]


def create_task(title: str, notes: str = "", due: str = "", tasklist_id: str = "@default") -> dict:
    """
    Create a new task in a task list.
    due should be RFC 3339 format e.g. "2026-03-01T00:00:00.000Z"
    """
    service = get_tasks_service()

    body = {"title": title}
    if notes:
        body["notes"] = notes
    if due:
        body["due"] = due

    try:
        # type: ignore[attr-defined] - Google API dynamically generates methods
        task = service.tasks().insert(
            tasklist = tasklist_id,
            body     = body
        ).execute()

        return {
            "success": True,
            "task_id": task["id"],
            "title":   task["title"]
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def complete_task(task_id: str, tasklist_id: str = "@default") -> dict:
    """Mark a task as completed."""
    service = get_tasks_service()

    try:
        # type: ignore[attr-defined] - Google API dynamically generates methods
        task = service.tasks().patch(
            tasklist = tasklist_id,
            task     = task_id,
            body     = {"status": "completed"}
        ).execute()

        return {"success": True, "title": task.get("title", "")}
    except Exception as e:
        return {"success": False, "error": str(e)}
