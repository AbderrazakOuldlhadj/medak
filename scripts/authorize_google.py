import os
import sys
import glob
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

sys.stdout.reconfigure(encoding='utf-8')

# Define OAuth Scopes (Drive & Sheets & Basic Profile)
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
    'openid',
    'https://www.googleapis.com/auth/userinfo.email'
]

def main():
    client_secrets = glob.glob('client_secret_*.json')
    if not client_secrets:
        client_secrets = glob.glob('*.json')
        client_secrets = [f for f in client_secrets if 'client_secret' in f or 'installed' in open(f, encoding='utf-8').read()]

    if not client_secrets:
        print("Error: No Google client secret JSON file found in the project root.")
        return

    client_secret_file = client_secrets[0]
    print(f"Using Client Secret File: {client_secret_file}")

    creds = None
    token_file = 'token.json'

    if os.path.exists(token_file):
        try:
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        except Exception:
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired token...")
            creds.refresh(Request())
        else:
            print("\nStarting Google OAuth Authorization server...")
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, SCOPES)
            
            # Print authorization instructions
            auth_url, _ = flow.authorization_url(prompt='consent')
            print("\n" + "="*70)
            print("PLEASE AUTHORIZE GOOGLE CONNECTION IN YOUR BROWSER:")
            print("The authorization page should automatically open in your default browser.")
            print(f"If it does not open, click or visit this link:\n{auth_url}")
            print("="*70 + "\n")
            
            creds = flow.run_local_server(port=0, prompt='consent')

        with open(token_file, 'w', encoding='utf-8') as token:
            token.write(creds.to_json())
        print(f"\n✅ Authorization successful! Token saved to {token_file}")

    print("\n✅ Google API Connection Verified & Ready!")

if __name__ == '__main__':
    main()
