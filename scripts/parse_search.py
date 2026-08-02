import json
import re
import urllib.parse
from bs4 import BeautifulSoup

with open('search_parfum.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
text = soup.get_text(separator="\n", strip=True)

with open('search_parfum_text.txt', 'w', encoding='utf-8') as f:
    f.write(text)

# Find all ad library IDs
ad_ids = set(re.findall(r'id=(\d{10,})', html))
print(f"Total Ad IDs found: {len(ad_ids)}")

# Find all l.facebook redirect links
l_links = set(re.findall(r'l\.facebook\.com/l\.php\?u=([^&"\']+)', html))
print(f"Total landing page links found: {len(l_links)}")

clean_landing_pages = []
for link in l_links:
    decoded = urllib.parse.unquote(link)
    if "facebook.com" not in decoded and "instagram.com" not in decoded:
        clean_landing_pages.append(decoded)
        print("Landing page:", decoded)

print(f"Unique store landing pages: {len(clean_landing_pages)}")
