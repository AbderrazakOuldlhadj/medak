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

collection_list = data.get('collectionList', [])
collections = data.get('collections', [])

# Map UID to items
col_by_uid = {col.get('uid'): col for col in collections}

print("COLLECTION DETAILED BREAKDOWN:")
for idx, item in enumerate(collection_list, 1):
    uid = item.get('uid')
    title = item.get('title')
    slug = item.get('slug')
    link = item.get('link')
    thumbnail = item.get('thumbnail')
    
    col_data = col_by_uid.get(uid, {})
    items = col_data.get('items', [])
    
    print(f"\n### {idx}. {title}")
    print(f"- **Slug**: `{slug}`")
    print(f"- **Total Products**: {len(items)}")
    if items:
        sample_names = [f"'{p.get('title').strip()}' ({p.get('price')} DZD)" for p in items[:5]]
        print(f"- **Sample Products**: {', '.join(sample_names)}")
