import os
import sys
import json
import requests

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.dirname(__file__))

SPREADSHEET_ID = "1bNNR9wgq0rw4cNeP8SEU-WlXCxx1pe-5_1aWq_YXO_A"

def detailed_inspect():
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
    print(f"Frozen Rows: {grid_props.get('frozenRowCount', 0)}")
    print(f"Frozen Columns: {grid_props.get('frozenColumnCount', 0)}")
    
    grid_data = sheet.get('data', [])[0]
    col_meta = grid_data.get('columnMetadata', [])
    row_meta = grid_data.get('rowMetadata', [])
    
    print("\n=== COLUMN WIDTHS ===")
    for idx, c in enumerate(col_meta[:15]):
        col_letter = chr(ord('A')+idx) if idx < 26 else f"Col{idx}"
        print(f"Col {col_letter}: {c.get('pixelSize')} px")
        
    print("\n=== ROW HEIGHTS (Header + Data) ===")
    for idx, r in enumerate(row_meta[:15]):
        print(f"Row {idx+1}: {r.get('pixelSize')} px")
        
    c_formats = sheet.get('conditionalFormats', [])
    print(f"\n=== CONDITIONAL FORMATTING ({len(c_formats)}) ===")
    print(json.dumps(c_formats, indent=2))
    
    basic_filter = sheet.get('basicFilter', {})
    print(f"\n=== BASIC FILTER ===")
    print(json.dumps(basic_filter, indent=2))

    banded = sheet.get('bandedRanges', [])
    print(f"\n=== BANDED RANGES ({len(banded)}) ===")
    print(json.dumps(banded, indent=2))

    row_data = grid_data.get('rowData', [])
    print("\n=== ALL CELLS (ROW 1 TO 15, ALL COLUMNS) ===")
    for r_idx in range(min(15, len(row_data))):
        row = row_data[r_idx]
        cells = row.get('values', [])
        print(f"\n--- ROW {r_idx+1} ---")
        for c_idx, cell in enumerate(cells):
            col_letter = chr(ord('A')+c_idx) if c_idx < 26 else f"Col{c_idx}"
            val = cell.get('formattedValue', '')
            user_val = cell.get('userEnteredValue')
            user_fmt = cell.get('userEnteredFormat')
            eff_fmt = cell.get('effectiveFormat')
            dv = cell.get('dataValidation')
            note = cell.get('note')
            
            if val or user_fmt or user_val or dv or note:
                print(f"Cell {col_letter}{r_idx+1}:")
                print(f"  Formatted Value: '{val}'")
                if user_val:
                    print(f"  User Value: {user_val}")
                if dv:
                    print(f"  Data Validation: {dv}")
                if note:
                    print(f"  Note: {note}")
                if user_fmt:
                    print(f"  userEnteredFormat: {json.dumps(user_fmt)}")
                if eff_fmt:
                    bg = eff_fmt.get('backgroundColor')
                    tf = eff_fmt.get('textFormat')
                    align = eff_fmt.get('horizontalAlignment')
                    valign = eff_fmt.get('verticalAlignment')
                    wrap = eff_fmt.get('wrapStrategy')
                    num_fmt = eff_fmt.get('numberFormat')
                    borders = eff_fmt.get('borders')
                    print(f"  Summary: bg={bg}, align={align}/{valign}, wrap={wrap}, numFmt={num_fmt}, borders={borders}")

if __name__ == '__main__':
    detailed_inspect()
