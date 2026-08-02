import os
import sys
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
    creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    drive_service = build('drive', 'v3', credentials=creds)

    query = "mimeType='application/vnd.google-apps.spreadsheet' and trashed=false"
    
    all_files = []
    page_token = None
    
    while True:
        results = drive_service.files().list(
            q=query,
            pageSize=100,
            pageToken=page_token,
            orderBy="modifiedTime desc",
            fields="nextPageToken, files(id, name, modifiedTime, webViewLink)"
        ).execute()

        all_files.extend(results.get('files', []))
        page_token = results.get('nextPageToken')
        if not page_token:
            break

    print(f"Total Sheets: {len(all_files)}\n")
    print("| # | Sheet Name | Last Modified (Date & Time) | Link |")
    print("|---|---|---|---|")
    for i, file in enumerate(all_files, start=1):
        name = file.get('name', 'Untitled').replace('|', '-')
        mod = file.get('modifiedTime', '').replace('T', ' ').replace('Z', '')
        link = file.get('webViewLink')
        print(f"| {i} | **{name}** | `{mod}` | [Open Sheet]({link}) |")

if __name__ == '__main__':
    main()
