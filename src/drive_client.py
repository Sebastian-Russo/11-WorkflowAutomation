"""
Think of this like a librarian who knows where every file in your
filing cabinet is. You describe what you're looking for and they
find it, tell you what's in it, and hand you a summary.

Drive readonly — we can search and read, not modify.
"""

from googleapiclient.discovery import build
from src.auth import get_credentials


def get_drive_service():
    return build("drive", "v3", credentials=get_credentials())


def search_files(query: str, max_results: int = 10) -> list[dict]:
    """
    Search Google Drive files by name or content.

    Uses Drive query syntax:
      "name contains 'budget'"
      "mimeType = 'application/vnd.google-apps.spreadsheet'"
      "modifiedTime > '2026-01-01'"
    """
    service = get_drive_service()

    result = service.files().list(
        q          = query,
        pageSize   = max_results,
        fields     = "files(id, name, mimeType, modifiedTime, webViewLink)"
    ).execute()

    files = result.get("files", [])

    return [
        {
            "id":           f["id"],
            "name":         f["name"],
            "type":         _readable_type(f["mimeType"]),
            "modified":     f.get("modifiedTime", ""),
            "link":         f.get("webViewLink", "")
        }
        for f in files
    ]


def get_file_content(file_id: str) -> dict:
    """
    Read the text content of a Google Doc or plain text file.
    Returns a summary-friendly truncated version.
    """
    service = get_drive_service()

    try:
        # Export Google Docs as plain text
        content = service.files().export(
            fileId   = file_id,
            mimeType = "text/plain"
        ).execute()

        # content is bytes — decode to string
        text = content.decode("utf-8") if isinstance(content, bytes) else content

        return {
            "success": True,
            "content": text[:3000]   # cap to keep tokens reasonable
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def _readable_type(mime_type: str) -> str:
    """Convert Google MIME types to human-readable labels."""
    types = {
        "application/vnd.google-apps.document":     "Google Doc",
        "application/vnd.google-apps.spreadsheet":  "Google Sheet",
        "application/vnd.google-apps.presentation": "Google Slides",
        "application/vnd.google-apps.folder":       "Folder",
        "application/pdf":                          "PDF",
        "text/plain":                               "Text file",
    }
    return types.get(mime_type, mime_type)
