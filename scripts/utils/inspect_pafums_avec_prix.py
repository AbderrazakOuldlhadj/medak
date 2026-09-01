import os
import sys
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
token_file = os.path.join(ROOT_DIR, "token.json")

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = Credentials.from_authorized_user_file(token_file, SCOPES)
service = build('sheets', 'v4', credentials=creds)

SPREADSHEET_ID = '1XJ3UN0Bg3iSejNiQ-6gXiMd0m-KnRll3Mk1noxa03Fw'
res = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range='A1:Z200').execute()
rows = res.get('values', [])

headers = rows[0] if rows else []
print("Headers:", headers)

valid_perfumes = []
for i, r in enumerate(rows[1:], start=2):
    brand = r[0].strip() if len(r) > 0 else ""
    name = r[1].strip() if len(r) > 1 else ""
    gros_price = r[2].strip() if len(r) > 2 else ""
    
    # Check if gros_price is valid (not '--', '—', empty)
    if gros_price and gros_price not in ['--', '—']:
        full_name = f"{brand} {name}".strip()
        valid_perfumes.append({
            'row': i,
            'brand': brand,
            'name': name,
            'full_name': full_name,
            'gros_price': gros_price
        })

print(f"\nTotal rows in sheet: {len(rows) - 1}")
print(f"Total valid perfumes with gros price: {len(valid_perfumes)}\n")

for p in valid_perfumes:
    print(f"Row {p['row']}: {p['full_name']} | Price (Gros): {p['gros_price']}")

output_file = os.path.join(ROOT_DIR, "data", "interim", "target_perfumes_from_sheet.json")
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(valid_perfumes, f, ensure_ascii=False, indent=2)

print(f"\nSaved target list to {output_file}")
