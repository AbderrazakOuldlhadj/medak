import glob
import re
import urllib.parse
import json
import csv
from bs4 import BeautifulSoup

def clean_url(raw_url):
    if not raw_url:
        return ""
    dec = urllib.parse.unquote(raw_url)
    # Remove tracking parameters like utm_source, utm_content, fbclid, etc. for cleaner URLs if desired, or keep exact
    return dec

# Load all html dumps
html_files = glob.glob("*.html")
print(f"Analyzing {len(html_files)} scraped HTML files for exact links...")

ad_card_records = []

for filepath in html_files:
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')
    
    # Extract all ad cards
    # Meta Ads Library ad cards usually contain "ID dans la bibliothèque" / "Library ID:" followed by number
    # and a link "Voir les détails de la publicité" / "See ad details" with href containing "id=..."
    
    for a in soup.find_all('a', href=True):
        href = a['href']
        if "ads/library/?id=" in href or "ads/library/banner/?id=" in href:
            full_ad_link = href if href.startswith("http") else f"https://www.facebook.com{href}"
            ad_id = re.search(r'id=(\d+)', href)
            if ad_id:
                ad_card_records.append({
                    'ad_id': ad_id.group(1),
                    'ad_link': full_ad_link
                })

print(f"Total verified Ad IDs found in page source: {len(ad_card_records)}")

# Extract all l.facebook landing page redirects
l_redirects = []
for filepath in html_files:
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()
    matches = re.findall(r'l\.facebook\.com/l\.php\?u=([^&"\']+)', html)
    for m in matches:
        url = urllib.parse.unquote(m)
        if not any(x in url for x in ["facebook.com", "instagram.com", "alibaba.com", "doubleclick", "cnct.fr", "itunes.apple.com", "google.com", "belezanaweb", "ustraa", "prospekt"]):
            l_redirects.append(url)

print(f"Total clean destination landing page URLs found: {len(l_redirects)}")

# Display sample verified destination URLs
print("\nVerified Landing Page URLs:")
for u in sorted(list(set(l_redirects))):
    print("-", u)
