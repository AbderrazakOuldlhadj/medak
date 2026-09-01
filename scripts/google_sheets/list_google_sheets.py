import os
import sys
import glob
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sys.stdout.reconfigure(encoding='utf-8')

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
    'openid',
    'https://www.googleapis.com/auth/userinfo.email'
]

def main():
    token_file = 'token.json'
    if not os.path.exists(token_file):
        print("Error: token.json not found. Please run authorize_google.py first.")
        return

    creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    
    # Build Drive API client
    drive_service = build('drive', 'v3', credentials=creds)

    # Query for all Google Sheets files
    query = "mimeType='application/vnd.google-apps.spreadsheet' and trashed=false"
    results = drive_service.files().list(
        q=query,
        pageSize=100,
        fields="nextPageToken, files(id, name, createdTime, modifiedTime, webViewLink, owners)"
    ).execute()

    files = results.get('files', [])

    print(f"\n=================== YOUR GOOGLE SHEETS ({len(files)} found) ===================")
    if not files:
        print("No Google Sheets found in your Google Drive.")
        return

    for i, file in enumerate(files, start=1):
        name = file.get('name')
        file_id = file.get('id')
        link = file.get('webViewLink')
        modified = file.get('modifiedTime', '')[:10]
        print(f"{i}. {name}")
        print(f"   ID: {file_id}")
        print(f"   Link: {link}")
        print(f"   Last Modified: {modified}")
        print("-" * 50)

if __name__ == '__main__':
    main()
