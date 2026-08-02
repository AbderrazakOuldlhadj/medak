import os
import sys
import json
import requests

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.dirname(__file__))

SPREADSHEET_ID = "1bNNR9wgq0rw4cNeP8SEU-WlXCxx1pe-5_1aWq_YXO_A"

def check_header_rules():
    token_file = os.path.join(os.path.dirname(__file__), '..', 'token.json')
    with open(token_file, 'r') as f:
        token_data = json.load(f)
    
    access_token = token_data.get('token')
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }
    
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}?includeGridData=true"
    res = requests.get(url, headers=headers)
    data = res.json()
    sheet = data['sheets'][0]
    grid_props = sheet['properties'].get('gridProperties', {})
    
    print("=== GRID PROPERTIES ===")
    print(json.dumps(grid_props, indent=2))
    
    print("\n=== CONDITIONAL FORMATTING ===")
    print(json.dumps(sheet.get('conditionalFormats', []), indent=2))

    print("\n=== BANDED RANGES ===")
    print(json.dumps(sheet.get('bandedRanges', []), indent=2))

    print("\n=== BASIC FILTER ===")
    print(json.dumps(sheet.get('basicFilter', {}), indent=2))

if __name__ == '__main__':
    check_header_rules()
