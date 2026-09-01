import sys
import json
import base64
import urllib.parse
import re
import urllib.request
import concurrent.futures
import time

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
                if col_name not in products_by_id[p_id]['collections']:
                    products_by_id[p_id]['collections'].append(col_name)

print(f"Total unique products to fetch: {len(products_by_id)}")

def fetch_product_details(p_id, p_info):
    slug = p_info['item_summary'].get('slug')
    url = f"https://perfumecorner.myecomstore.net/products/{slug}"
    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    )
    
    result = {
        'id': p_id,
        'slug': slug,
        'url': url,
        'collections': p_info['collections'],
        'summary': p_info['item_summary'],
        'product_details': None,
        'success': False,
        'error': None
    }
    
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                html = resp.read().decode('utf-8')
            matches = re.findall(r'decodeURIComponent\(atob\(["\']([A-Za-z0-9+/=]+)["\']\)\)', html)
            if matches:
                decoded_b = base64.b64decode(matches[0])
                decoded_s = urllib.parse.unquote(decoded_b.decode('utf-8', errors='ignore'))
                prod_data = json.loads(decoded_s)
                product = prod_data.get('product')
                if product:
                    result['product_details'] = product
                    result['success'] = True
                    return result
        except Exception as e:
            result['error'] = str(e)
            time.sleep(1)
            
    return result

print("Starting concurrent fetching of product details...")
start_time = time.time()
detailed_products = []

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = {executor.submit(fetch_product_details, p_id, p_info): p_id for p_id, p_info in products_by_id.items()}
    for future in concurrent.futures.as_completed(futures):
        res = future.result()
        detailed_products.append(res)
        print(f"[{len(detailed_products)}/{len(products_by_id)}] Fetched: {res['slug']} - Success: {res['success']}")

print(f"\nFinished in {time.time() - start_time:.2f}s")
success_count = sum(1 for p in detailed_products if p['success'])
print(f"Success: {success_count} / {len(detailed_products)}")

# Save intermediate json to scratch/
output_json_path = r"C:\Users\msipc\.gemini\antigravity-ide\brain\58560254-acba-49bf-8e1f-2bbf9072ba56\scratch\scraped_products.json"
with open(output_json_path, "w", encoding="utf-8") as f:
    json.dump(detailed_products, f, ensure_ascii=False, indent=2)
print("Saved raw JSON to", output_json_path)

