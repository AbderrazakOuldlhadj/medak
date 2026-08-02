import os
import sys
import gspread
from google.oauth2.credentials import Credentials

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
    gc = gspread.authorize(creds)
    
    print("Testing creating a sheet directly...")
    try:
        sh = gc.create("Test Sheet Connection")
        print(f"Success! Created sheet URL: {sh.url}")
    except Exception as e:
        print("Sheets API error:", e)

if __name__ == '__main__':
    main()
