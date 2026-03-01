"""
Think of this like a spreadsheet assistant who can read your
tables, add new rows, and update existing cells — without you
ever having to open the file yourself.

Sheets API works with ranges in A1 notation:
  "Sheet1!A1:D10" = Sheet1, columns A-D, rows 1-10
  "Sheet1!A:A"    = entire column A
  "Sheet1!1:1"    = entire row 1
"""

from googleapiclient.discovery import build
from src.auth import get_credentials


def get_sheets_service():
    return build("sheets", "v4", credentials=get_credentials())


def get_sheet_values(spreadsheet_id: str, range_name: str = "Sheet1") -> dict:
    """
    Read values from a spreadsheet range.

    spreadsheet_id: the ID from the spreadsheet URL
      e.g. https://docs.google.com/spreadsheets/d/[THIS_PART]/edit
    range_name: A1 notation range, defaults to entire Sheet1
    """
    service = get_sheets_service()

    try:
        result = service.spreadsheets().values().get(
            spreadsheetId = spreadsheet_id,
            range         = range_name
        ).execute()

        rows = result.get("values", [])

        if not rows:
            return {"success": True, "data": [], "row_count": 0}

        # First row is usually headers — label each row with them
        headers = rows[0] if rows else []
        data    = []
        for row in rows[1:]:
            # Pad short rows with empty strings to match header count
            padded = row + [""] * (len(headers) - len(row))
            data.append(dict(zip(headers, padded)))

        return {
            "success":   True,
            "headers":   headers,
            "data":      data[:50],    # cap at 50 rows to keep tokens reasonable
            "row_count": len(rows) - 1
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def append_row(spreadsheet_id: str, values: list, range_name: str = "Sheet1") -> dict:
    """
    Append a new row to a spreadsheet.

    values: list of cell values in order e.g. ["2026-03-01", "Groceries", "45.00"]
    """
    service = get_sheets_service()

    try:
        result = service.spreadsheets().values().append(
            spreadsheetId    = spreadsheet_id,
            range            = range_name,
            valueInputOption = "USER_ENTERED",   # interprets dates, numbers correctly
            body             = {"values": [values]}
        ).execute()

        return {
            "success":      True,
            "updated_range": result["updates"]["updatedRange"],
            "rows_added":   result["updates"]["updatedRows"]
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def update_cell(spreadsheet_id: str, cell: str, value: str) -> dict:
    """
    Update a single cell value.

    cell: A1 notation e.g. "Sheet1!B5"
    """
    service = get_sheets_service()

    try:
        service.spreadsheets().values().update(
            spreadsheetId    = spreadsheet_id,
            range            = cell,
            valueInputOption = "USER_ENTERED",
            body             = {"values": [[value]]}
        ).execute()

        return {"success": True, "cell": cell, "value": value}
    except Exception as e:
        return {"success": False, "error": str(e)}
