import sys
import json
import base64
import urllib.parse
import re

sys.stdout.reconfigure(encoding='utf-8')

content_path = r"C:\Users\msipc\.gemini\antigravity-ide\brain\58560254-acba-49bf-8e1f-2bbf9072ba56\.system_generated\steps\5\content.md"

with open(content_path, "r", encoding="utf-8") as f:
    text = f.read()

matches = re.findall(r'decodeURIComponent\(atob\(["\']([A-Za-z0-9+/=]+)["\']\)\)', text)
decoded_bytes = base64.b64decode(matches[0])
decoded_str = urllib.parse.unquote(decoded_bytes.decode('utf-8', errors='ignore'))
data = json.loads(decoded_str)

collections = data.get('collections', [])

target_cols = {
    'Best-Seller': 'الأكثر طلبا - Best Seller',
    'parfum-european': 'العطور الأوروبية'
}

products_by_id = {}

for col in collections:
    col_slug = col.get('slug')
    if col_slug in target_cols:
        col_name = target_cols[col_slug]
        for item in col.get('items', []):
            p_id = item.get('id')
            if p_id not in products_by_id:
                products_by_id[p_id] = {
                    'item_summary': item,
                    'collections': [col_name]
                }
            else:
                products_by_id[p_id]['collections'].append(col_name)

print(f"Total unique products across both collections: {len(products_by_id)}")
for p_id, p_info in list(products_by_id.items())[:10]:
    print(f"ID: {p_id} | Title: {p_info['item_summary'].get('title')} | Slug: {p_info['item_summary'].get('slug')} | Collections: {p_info['collections']}")

