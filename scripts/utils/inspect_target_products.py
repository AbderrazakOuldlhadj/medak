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
target_slugs = ['Best-Seller', 'parfum-european']

for col in collections:
    if col.get('slug') in target_slugs:
        print(f"=== Collection: {col.get('name')} ({col.get('slug')}) ===")
        items = col.get('items', [])
        print(f"Items count: {len(items)}")
        if items:
            print("First item full JSON:")
            print(json.dumps(items[0], indent=2, ensure_ascii=False))
            print("Second item full JSON:")
            print(json.dumps(items[1], indent=2, ensure_ascii=False))

