import sys
import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sys.stdout.reconfigure(encoding='utf-8')

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
    'openid',
    'https://www.googleapis.com/auth/userinfo.email'
]

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
TOKEN_FILE = os.path.join(ROOT_DIR, 'token.json')

def get_services():
    if not os.path.exists(TOKEN_FILE):
        raise FileNotFoundError(f"token.json not found at {TOKEN_FILE}")
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    drive_service = build('drive', 'v3', credentials=creds)
    sheets_service = build('sheets', 'v4', credentials=creds)
    return drive_service, sheets_service

def list_recent_sheets():
    drive, _ = get_services()
    res = drive.files().list(
        q="mimeType='application/vnd.google-apps.spreadsheet' and trashed=false",
        pageSize=10,
        orderBy="modifiedTime desc",
        fields="files(id, name, modifiedTime, webViewLink)"
    ).execute()
    files = res.get('files', [])
    print(f"Found {len(files)} recent Google Sheets:")
    for f in files:
        print(f"Name: '{f['name']}' | ID: {f['id']} | Modified: {f['modifiedTime']}")
    return files

if __name__ == '__main__':
    list_recent_sheets()
