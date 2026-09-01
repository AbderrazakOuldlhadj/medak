import os
import sys
import csv
import glob

# Ensure UTF-8 output encoding for Windows terminal
sys.stdout.reconfigure(encoding='utf-8')

sys.path.append(os.path.dirname(__file__))
import google_sheets_mcp as mcp_mod

SPREADSHEET_TITLE = "Algeria Parfums Ads Research"
CSV_PATH = os.path.join(os.path.dirname(__file__), '..', 'ads_research.csv')

def create_and_format_ads_sheet():
    drive_service = mcp_mod.get_drive_service()
    sheets_service = mcp_mod.get_sheets_service()

    # Search if sheet already exists
    query = f"name = '{SPREADSHEET_TITLE}' and mimeType = 'application/vnd.google-apps.spreadsheet' and trashed = false"
    results = drive_service.files().list(q=query, fields="files(id, name, webViewLink)").execute()
    files = results.get('files', [])

    if files:
        spreadsheet_id = files[0]['id']
        url = files[0]['webViewLink']
        print(f"Found existing Google Sheet: '{SPREADSHEET_TITLE}'")
    else:
        spreadsheet = {'properties': {'title': SPREADSHEET_TITLE}}
        res = sheets_service.spreadsheets().create(body=spreadsheet, fields='spreadsheetId,spreadsheetUrl').execute()
        spreadsheet_id = res.get('spreadsheetId')
        url = res.get('spreadsheetUrl')
        print(f"Created new Google Sheet: '{SPREADSHEET_TITLE}'")

    # Read CSV data
    with open(CSV_PATH, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        data = [row for row in reader if any(row)]

    num_rows = len(data)
    num_cols = len(data[0]) if num_rows > 0 else 0

    print(f"Uploading {num_rows - 1} rows of data...")

    # Clear existing sheet content first
    sheets_service.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id,
        range='Sheet1!A1:Z100',
        body={}
    ).execute()

    # Update cell values
    sheets_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range='Sheet1!A1',
        valueInputOption='USER_ENTERED',
        body={'values': data}
    ).execute()

    # Format sheet properties and styles
    sheet_metadata = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheet_id = sheet_metadata['sheets'][0]['properties']['sheetId']

    requests = [
        # Set column widths
        {"updateDimensionProperties": {"range": {"sheetId": sheet_id, "dimension": "COLUMNS", "startIndex": 0, "endIndex": 1}, "properties": {"pixelSize": 150}, "fields": "pixelSize"}},
        {"updateDimensionProperties": {"range": {"sheetId": sheet_id, "dimension": "COLUMNS", "startIndex": 1, "endIndex": 2}, "properties": {"pixelSize": 340}, "fields": "pixelSize"}},
        {"updateDimensionProperties": {"range": {"sheetId": sheet_id, "dimension": "COLUMNS", "startIndex": 2, "endIndex": 3}, "properties": {"pixelSize": 130}, "fields": "pixelSize"}},
        {"updateDimensionProperties": {"range": {"sheetId": sheet_id, "dimension": "COLUMNS", "startIndex": 3, "endIndex": 4}, "properties": {"pixelSize": 110}, "fields": "pixelSize"}},
        {"updateDimensionProperties": {"range": {"sheetId": sheet_id, "dimension": "COLUMNS", "startIndex": 4, "endIndex": 5}, "properties": {"pixelSize": 260}, "fields": "pixelSize"}},
        {"updateDimensionProperties": {"range": {"sheetId": sheet_id, "dimension": "COLUMNS", "startIndex": 5, "endIndex": 6}, "properties": {"pixelSize": 260}, "fields": "pixelSize"}},
        {"updateDimensionProperties": {"range": {"sheetId": sheet_id, "dimension": "COLUMNS", "startIndex": 6, "endIndex": 7}, "properties": {"pixelSize": 140}, "fields": "pixelSize"}},
        
        # Header formatting (Dark Navy background, white bold text, centered)
        {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 0,
                    "endRowIndex": 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": num_cols
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 0.10, "green": 0.18, "blue": 0.36},
                        "textFormat": {
                            "fontSize": 11,
                            "bold": True,
                            "foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}
                        },
                        "horizontalAlignment": "CENTER",
                        "verticalAlignment": "MIDDLE"
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)"
            }
        },
        # Row height for header
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": sheet_id,
                    "dimension": "ROWS",
                    "startIndex": 0,
                    "endIndex": 1
                },
                "properties": {
                    "pixelSize": 40
                },
                "fields": "pixelSize"
            }
        },
        # Alignment for data rows
        {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 1,
                    "endRowIndex": num_rows,
                    "startColumnIndex": 2,
                    "endColumnIndex": 4
                },
                "cell": {
                    "userEnteredFormat": {
                        "horizontalAlignment": "CENTER",
                        "verticalAlignment": "MIDDLE"
                    }
                },
                "fields": "userEnteredFormat(horizontalAlignment,verticalAlignment)"
            }
        },
        {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 1,
                    "endRowIndex": num_rows,
                    "startColumnIndex": 6,
                    "endColumnIndex": 7
                },
                "cell": {
                    "userEnteredFormat": {
                        "horizontalAlignment": "CENTER",
                        "verticalAlignment": "MIDDLE"
                    }
                },
                "fields": "userEnteredFormat(horizontalAlignment,verticalAlignment)"
            }
        },
        # Enable Filter View
        {
            "setBasicFilter": {
                "filter": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": 0,
                        "endRowIndex": num_rows,
                        "startColumnIndex": 0,
                        "endColumnIndex": num_cols
                    }
                }
            }
        }
    ]

    sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': requests}
    ).execute()

    print("\n" + "="*70)
    print("Google Sheet created and formatted successfully!")
    print(f"Spreadsheet ID: {spreadsheet_id}")
    print(f"Spreadsheet URL: {url}")
    print("="*70)
    return url

if __name__ == '__main__':
    create_and_format_ads_sheet()
