"""
Think of this like a document assistant who can read any of your
Google Docs, create new ones, add content, find specific sections,
and format text — all without you ever opening the file yourself.

The Docs API works through "requests" — a list of operations sent
in one batch. Think of it like giving someone a marked-up printout:
"bold this, delete that, insert this here" — all at once.
"""

from googleapiclient.discovery import build
from src.auth import get_credentials


def get_docs_service():
    return build("docs", "v1", credentials=get_credentials())


def get_document(document_id: str) -> dict:
    """
    Read the full text content of a Google Doc.

    document_id: the ID from the document URL
      e.g. https://docs.google.com/document/d/[THIS_PART]/edit
    """
    service = get_docs_service()

    try:
        doc   = service.documents().get(documentId=document_id).execute()
        text  = _extract_text(doc)
        title = doc.get("title", "Untitled")

        return {
            "success":     True,
            "title":       title,
            "content":     text[:4000],
            "full_length": len(text)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def create_document(title: str, content: str) -> dict:
    """Create a new Google Doc with the given title and content."""
    service = get_docs_service()

    try:
        doc         = service.documents().create(body={"title": title}).execute()
        document_id = doc["documentId"]

        service.documents().batchUpdate(
            documentId = document_id,
            body       = {
                "requests": [{
                    "insertText": {
                        "location": {"index": 1},
                        "text":     content
                    }
                }]
            }
        ).execute()

        return {
            "success":     True,
            "document_id": document_id,
            "title":       title,
            "link":        f"https://docs.google.com/document/d/{document_id}/edit"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def append_to_document(document_id: str, content: str) -> dict:
    """
    Append text to the end of an existing Google Doc.

    Reads the current document length first to find the correct
    insertion index — Google Docs requires exact character positions
    for all edits, unlike a simple file append.
    """
    service = get_docs_service()

    try:
        doc          = service.documents().get(documentId=document_id).execute()
        content_list = doc.get("body", {}).get("content", [])

        # Last element's endIndex minus 1 = safe insertion point at end
        # Google always reserves the final index for the document itself
        end_index = content_list[-1].get("endIndex", 1) - 1

        service.documents().batchUpdate(
            documentId = document_id,
            body       = {
                "requests": [{
                    "insertText": {
                        "location": {"index": end_index},
                        "text":     "\n" + content
                    }
                }]
            }
        ).execute()

        return {"success": True, "document_id": document_id}
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_headings(document_id: str) -> dict:
    """
    Extract all headings from a Google Doc to understand its structure.

    Useful before reading a long doc — lets Claude know what sections
    exist so it can target the right one rather than reading everything.
    """
    service = get_docs_service()

    try:
        doc      = service.documents().get(documentId=document_id).execute()
        headings = []

        for block in doc.get("body", {}).get("content", []):
            paragraph = block.get("paragraph", {})
            style     = paragraph.get("paragraphStyle", {}).get("namedStyleType", "")

            # Heading styles are HEADING_1 through HEADING_6
            if style.startswith("HEADING"):
                text = "".join(
                    e.get("textRun", {}).get("content", "")
                    for e in paragraph.get("elements", [])
                ).strip()

                if text:
                    headings.append({
                        "level": style,
                        "text":  text
                    })

        return {"success": True, "headings": headings, "count": len(headings)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def search_in_document(document_id: str, search_term: str) -> dict:
    """
    Find all occurrences of a search term within a Google Doc.

    Returns the surrounding context for each match so Claude can
    understand what section the term appears in.
    """
    service = get_docs_service()

    try:
        doc  = service.documents().get(documentId=document_id).execute()
        text = _extract_text(doc)

        matches = []
        term    = search_term.lower()
        text_lower = text.lower()
        start   = 0

        while True:
            idx = text_lower.find(term, start)
            if idx == -1:
                break

            # Extract surrounding context — 150 chars before and after
            context_start = max(0, idx - 150)
            context_end   = min(len(text), idx + len(search_term) + 150)
            matches.append({
                "position": idx,
                "context":  text[context_start:context_end]
            })
            start = idx + 1

        return {
            "success": True,
            "term":    search_term,
            "count":   len(matches),
            "matches": matches[:10]   # cap at 10 matches
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def format_text(document_id: str, text_to_find: str, bold: bool = False,
                italic: bool = False, heading_level: int = None) -> dict:
    """
    Apply formatting to text in a Google Doc.

    Finds the first occurrence of text_to_find and applies formatting.
    bold/italic: apply text styling
    heading_level: 1-6 to apply a heading style (overrides bold/italic)

    The Docs API requires knowing exact character positions — we find
    the text first, then send formatting requests targeting those positions.
    """
    service = get_docs_service()

    try:
        doc      = service.documents().get(documentId=document_id).execute()
        full_text = _extract_text(doc)

        # Find the text position
        idx = full_text.find(text_to_find)
        if idx == -1:
            return {"success": False, "error": f"Text '{text_to_find}' not found in document"}

        start_idx = idx + 1      # Docs API uses 1-based indexing
        end_idx   = idx + len(text_to_find) + 1

        requests = []

        if heading_level and 1 <= heading_level <= 6:
            # Apply heading paragraph style
            requests.append({
                "updateParagraphStyle": {
                    "range": {"startIndex": start_idx, "endIndex": end_idx},
                    "paragraphStyle": {
                        "namedStyleType": f"HEADING_{heading_level}"
                    },
                    "fields": "namedStyleType"
                }
            })
        else:
            # Apply character formatting
            text_style = {}
            fields     = []

            if bold:
                text_style["bold"] = True
                fields.append("bold")
            if italic:
                text_style["italic"] = True
                fields.append("italic")

            if text_style:
                requests.append({
                    "updateTextStyle": {
                        "range":     {"startIndex": start_idx, "endIndex": end_idx},
                        "textStyle": text_style,
                        "fields":    ",".join(fields)
                    }
                })

        if not requests:
            return {"success": False, "error": "No formatting specified"}

        service.documents().batchUpdate(
            documentId = document_id,
            body       = {"requests": requests}
        ).execute()

        return {"success": True, "formatted": text_to_find}
    except Exception as e:
        return {"success": False, "error": str(e)}


def delete_content(document_id: str, text_to_delete: str) -> dict:
    """
    Delete a specific section of text from a Google Doc.

    Finds the first occurrence of text_to_delete and removes it.
    Use carefully — this is permanent and cannot be undone via API.
    """
    service = get_docs_service()

    try:
        doc       = service.documents().get(documentId=document_id).execute()
        full_text = _extract_text(doc)

        idx = full_text.find(text_to_delete)
        if idx == -1:
            return {"success": False, "error": f"Text '{text_to_delete}' not found"}

        start_idx = idx + 1
        end_idx   = idx + len(text_to_delete) + 1

        service.documents().batchUpdate(
            documentId = document_id,
            body       = {
                "requests": [{
                    "deleteContentRange": {
                        "range": {
                            "startIndex": start_idx,
                            "endIndex":   end_idx
                        }
                    }
                }]
            }
        ).execute()

        return {"success": True, "deleted": text_to_delete}
    except Exception as e:
        return {"success": False, "error": str(e)}


def _extract_text(doc: dict) -> str:
    """
    Walk Google Doc's nested content structure and extract plain text.

    A Google Doc is structured as:
      body → content → paragraphs → elements → textRun → content
    We flatten all of that into one clean string.
    """
    text = []
    for block in doc.get("body", {}).get("content", []):
        paragraph = block.get("paragraph", {})
        for element in paragraph.get("elements", []):
            content = element.get("textRun", {}).get("content", "")
            if content:
                text.append(content)
    return "".join(text)
