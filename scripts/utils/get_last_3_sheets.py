import os
import sys
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
token_file = os.path.join(ROOT_DIR, "token.json")

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

creds = Credentials.from_authorized_user_file(token_file, SCOPES)
drive = build('drive', 'v3', credentials=creds)

query = "mimeType='application/vnd.google-apps.spreadsheet' and trashed=false"
results = drive.files().list(
    q=query,
    orderBy='modifiedTime desc',
    pageSize=3,
    fields='files(id, name, modifiedTime, webViewLink, createdTime)'
).execute()

files = results.get('files', [])
print(json.dumps(files, indent=2, ensure_ascii=False))
