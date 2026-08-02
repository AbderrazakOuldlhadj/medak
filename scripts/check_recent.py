import os
import sys
import json
import requests

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.dirname(__file__))

def check_all_sheets_and_modified_spreadsheets():
    token_file = os.path.join(os.path.dirname(__file__), '..', 'token.json')
    with open(token_file, 'r') as f:
        token_data = json.load(f)
    
    access_token = token_data.get('token')
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }
    
    # 1. Drive list recently modified sheets
    drive_url = "https://www.googleapis.com/drive/v3/files?q=mimeType='application/vnd.google-apps.spreadsheet' and trashed=false&orderBy=modifiedTime desc&pageSize=5&fields=files(id,name,modifiedTime,webViewLink)"
    res = requests.get(drive_url, headers=headers)
    files = res.json().get('files', [])
    print("=== RECENTLY MODIFIED SPREADSHEETS ===")
    for f in files:
        print(f"Name: {f['name']} | ID: {f['id']} | Modified: {f['modifiedTime']} | Link: {f['webViewLink']}")
        
    # 2. Check all sheets/tabs in Algeria Parfums Ads Research (1bNNR9wgq0rw4cNeP8SEU-WlXCxx1pe-5_1aWq_YXO_A)
    sp_url = "https://sheets.googleapis.com/v4/spreadsheets/1bNNR9wgq0rw4cNeP8SEU-WlXCxx1pe-5_1aWq_YXO_A"
    res2 = requests.get(sp_url, headers=headers)
    sp_data = res2.json()
    sheets = sp_data.get('sheets', [])
    print(f"\n=== TABS IN 'Algeria Parfums Ads Research' ({len(sheets)} tabs) ===")
    for s in sheets:
        p = s['properties']
        print(f"Sheet ID: {p['sheetId']} | Title: '{p['title']}' | GridProperties: {p.get('gridProperties')}")

if __name__ == '__main__':
    check_all_sheets_and_modified_spreadsheets()
