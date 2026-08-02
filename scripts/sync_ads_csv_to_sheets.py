import os
import sys
import csv

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.dirname(__file__))
import google_sheets_mcp as mcp_mod

CSV_PATH = os.path.join(os.path.dirname(__file__), '..', 'ads_research.csv')
SPREADSHEET_ID = "1bNNR9wgq0rw4cNeP8SEU-WlXCxx1pe-5_1aWq_YXO_A"

def sync_csv_to_sheet():
    with open(CSV_PATH, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        data = [row for row in reader if any(row)]

    num_rows = len(data)
    num_cols = len(data[0]) if num_rows > 0 else 0

    print(f"Syncing {num_rows - 1} rows to Google Sheet...")

    sheets_service = mcp_mod.get_sheets_service()

    # Clear existing range Sheet1!A1:Z50
    sheets_service.spreadsheets().values().clear(
        spreadsheetId=SPREADSHEET_ID,
        range='Sheet1!A1:Z50',
        body={}
    ).execute()

    # Update cell values starting at A1
    sheets_service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range='Sheet1!A1',
        valueInputOption='USER_ENTERED',
        body={'values': data}
    ).execute()

    # Update basic filter range to cover new row count
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
                            'endColumnIndex': num_cols
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
    print("✅ Sync complete!")
    print(f"Spreadsheet Link: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit")
    print("="*70)

if __name__ == '__main__':
    sync_csv_to_sheet()
