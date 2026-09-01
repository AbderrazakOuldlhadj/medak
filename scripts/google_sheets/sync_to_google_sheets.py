import os
import csv
import glob
import gspread
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
    'openid',
    'https://www.googleapis.com/auth/userinfo.email'
]

def get_credentials():
    token_file = 'token.json'
    creds = None
    if os.path.exists(token_file):
        try:
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        except Exception:
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            client_secrets = glob.glob('client_secret_*.json')
            if not client_secrets:
                raise FileNotFoundError("Client secret JSON file not found!")
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets[0], SCOPES)
            creds = flow.run_local_server(port=0, prompt='consent')
            with open(token_file, 'w', encoding='utf-8') as token:
                token.write(creds.to_json())
    return creds

def sync_csv_to_sheet(csv_path="ads_research.csv", sheet_title="Algeria Parfums Ads Research"):
    creds = get_credentials()
    gc = gspread.authorize(creds)

    print(f"Connecting to Google Sheets...")
    # Try opening existing spreadsheet or create a new one
    try:
        sh = gc.open(sheet_title)
        print(f"Opened existing Google Sheet: '{sheet_title}'")
    except gspread.exceptions.SpreadsheetNotFound:
        sh = gc.create(sheet_title)
        print(f"Created new Google Sheet: '{sheet_title}'")

    worksheet = sh.get_worksheet(0)

    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        data = list(reader)

    worksheet.clear()
    worksheet.update(values=data, range_name='A1')
    
    print("\n" + "="*70)
    print(f"✅ Successfully synced {len(data)-1} rows to Google Sheets!")
    print(f"🔗 Spreadsheet Link: {sh.url}")
    print("="*70)

if __name__ == '__main__':
    sync_csv_to_sheet()
