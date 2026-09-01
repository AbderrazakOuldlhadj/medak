import sys
import json
import base64
import urllib.parse
import re
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')

url = "https://perfumecorner.myecomstore.net/products/strikeblackbyassafabsoluaventuscreedt-3b"
req = urllib.request.Request(
    url, 
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
)

try:
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode('utf-8')
    print("Page fetched, length:", len(html))
    matches = re.findall(r'decodeURIComponent\(atob\(["\']([A-Za-z0-9+/=]+)["\']\)\)', html)
    print(f"Found {len(matches)} data blocks")
    if matches:
        decoded_bytes = base64.b64decode(matches[0])
        decoded_str = urllib.parse.unquote(decoded_bytes.decode('utf-8', errors='ignore'))
        prod_data = json.loads(decoded_str)
        product = prod_data.get('product')
        print("Product keys:", list(product.keys()) if product else "None")
        if product:
            print("Title:", product.get('title'))
            print("Description:", product.get('description'))
            print("Images:", product.get('images'))
            print("Price:", product.get('price'))
            print("Variants:", product.get('variants'))
except Exception as e:
    print("Error:", e)

