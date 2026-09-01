import os
import sys
import json
import requests

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.dirname(__file__))

SPREADSHEET_ID = "1bNNR9wgq0rw4cNeP8SEU-WlXCxx1pe-5_1aWq_YXO_A"

def inspect_row1_and_2():
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
    grid_data = sheet.get('data', [])[0]
    row_data = grid_data.get('rowData', [])
    
    print("\n=== ROW 1 ===")
    row1 = row_data[0].get('values', [])
    for c_idx, cell in enumerate(row1[:7]):
        col_name = chr(ord('A')+c_idx)
        print(f"{col_name}1: '{cell.get('formattedValue')}' | userFmt={cell.get('userEnteredFormat')}")

    print("\n=== ROW 2 ===")
    row2 = row_data[1].get('values', [])
    for c_idx, cell in enumerate(row2[:7]):
        col_name = chr(ord('A')+c_idx)
        print(f"{col_name}2: '{cell.get('formattedValue')}' | userFmt={cell.get('userEnteredFormat')}")

if __name__ == '__main__':
    inspect_row1_and_2()
