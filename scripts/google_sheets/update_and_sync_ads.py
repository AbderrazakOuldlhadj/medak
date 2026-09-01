import os
import sys
import csv

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.dirname(__file__))
import google_sheets_mcp as mcp_mod

CSV_PATH = os.path.join(os.path.dirname(__file__), '..', 'ads_research.csv')
SPREADSHEET_ID = "1bNNR9wgq0rw4cNeP8SEU-WlXCxx1pe-5_1aWq_YXO_A"

def update_csv_and_sync():
    # Read existing CSV lines
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    print(f"Original CSV total lines: {len(lines)}")
    
    # 1-indexed lines to delete: 11, 13, 14
    lines_to_delete = {11, 13, 14}
    
    new_csv_rows = []
    for idx, line in enumerate(lines, start=1):
        if idx in lines_to_delete:
            print(f"Deleting line {idx}: {line.strip()}")
            continue
        if not line.strip():
            continue
        
        # Parse CSV line
        reader = list(csv.reader([line]))[0]
        if idx == 1:
            # Header row
            new_csv_rows.append(reader)
        else:
            # Data row: clear Ad Link (Column Index 5 / 6th column)
            if len(reader) >= 6:
                reader[5] = ""
            new_csv_rows.append(reader)

    # Save updated CSV
    with open(CSV_PATH, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(new_csv_rows)
        
    print(f"\nUpdated CSV saved to '{CSV_PATH}' with {len(new_csv_rows)-1} data rows.")

    # Get Sheets service with auto token refresh
    sheets_service = mcp_mod.get_sheets_service()

    # 1. Clear existing range Sheet1!A1:Z50
    sheets_service.spreadsheets().values().clear(
        spreadsheetId=SPREADSHEET_ID,
        range='Sheet1!A1:Z50',
        body={}
    ).execute()
    print("Cleared previous values range.")

    # 2. Update values A1 with new rows
    sheets_service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range='Sheet1!A1',
        valueInputOption='USER_ENTERED',
        body={'values': new_csv_rows}
    ).execute()
    print("Values updated successfully in Google Sheet!")

    # 3. Update basic filter range to cover new row count
    num_rows = len(new_csv_rows)
    filter_req = {
        'requests': [
            {
                'setBasicFilter': {
                    'filter': {
                        'range': {
                            'sheetId': 0,
                            'startRowIndex': 0,
                            'endRowIndex': num_rows,
                            'startColumnIndex': 0,
                            'endColumnIndex': 7
                        }
                    }
                }
            }
        ]
    }
    sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body=filter_req
    ).execute()
    
    print("\n" + "="*70)
    print("Successfully updated CSV and synced to Google Sheet!")
    print(f"Spreadsheet Link: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit")
    print("="*70)

if __name__ == '__main__':
    update_csv_and_sync()
