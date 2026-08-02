import glob
import re
import urllib.parse
import csv

html_files = glob.glob("search_*.html")

l_links = set()
for filepath in html_files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        matches = re.findall(r'l\.facebook\.com/l\.php\?u=([^&"\']+)', content)
        for m in matches:
            l_links.add(urllib.parse.unquote(m))

print(f"Total raw decoded links across all search dumps: {len(l_links)}")

stores = set()
for link in l_links:
    if not any(x in link for x in ["facebook.com", "instagram.com", "alibaba.com", "doubleclick", "cnct.fr", "itunes.apple.com", "google.com", "belezanaweb", "ustraa", "prospekt"]):
        stores.add(link)

print("\n--- Additional Algerian E-commerce Perfume Stores Discovered ---")
for s in sorted(list(stores))[:15]:
    print(s)
