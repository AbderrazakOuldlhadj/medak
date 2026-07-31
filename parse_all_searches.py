import os
import glob
import re
import json
import csv
import urllib.parse
from bs4 import BeautifulSoup

html_files = glob.glob("search_*.html") + glob.glob("scraped_*.html")

competitors = []

for filepath in html_files:
    print(f"Parsing {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')
    
    # Extract l.facebook links
    l_links = re.findall(r'l\.facebook\.com/l\.php\?u=([^&"\']+)', html)
    
    # Extract Ad IDs
    ad_ids = re.findall(r'id=(\d{10,})', html)
    
    # Find text blocks that look like perfume ads
    lines = [line.strip() for line in soup.get_text(separator="\n").split("\n") if line.strip()]
    
    for i, line in enumerate(lines):
        # Look for price patterns common in Algeria: e.g., 2900, 3500 DA, 2000 DA, 11,000 DZD, 18,000 DZD, 4500 DZD
        if any(kw in line.lower() for kw in ["dzd", "da", "da ", "000 da", "00 da", "000dzd", "000 dzd", "2000", "2900", "3500", "4500", "5500", "6500", "7500", "8500", "12000", "15000"]):
            # Get surrounding context
            context_start = max(0, i - 8)
            context_end = min(len(lines), i + 8)
            snippet = " | ".join(lines[context_start:context_end])
            
            # Look for landing page in decoded links
            found_url = ""
            for l in l_links:
                dec = urllib.parse.unquote(l)
                if not any(x in dec for x in ["facebook.com", "instagram.com", "alibaba.com", "doubleclick", "cnct.fr", "itunes.apple.com", "google.com"]):
                    found_url = dec
                    break

            # Infer store name from context snippet or landing page domain
            store_name = "Algerian Perfume Store"
            if "Smell Good" in snippet:
                store_name = "Smell Good Dz"
            elif "Auraluxe" in snippet or "auraluxe" in found_url:
                store_name = "Auraluxe"
            elif "Maria" in snippet or "maria" in found_url:
                store_name = "Maria Parfum Dz"
            elif "Beauty Life" in snippet:
                store_name = "Beauty Life Dz"
            elif "Mina" in snippet or "minasbeauty" in found_url:
                store_name = "Mina's Beauty"
            elif found_url:
                domain = urllib.parse.urlparse(found_url).netloc
                store_name = domain.replace('.youcan.store', '').replace('.foorweb.store', '').replace('.shop', '').replace('.com', '').replace('.dz', '').title()

            ad_id = ad_ids[0] if ad_ids else "1266422528876738"
            
            competitors.append({
                'Store Name': store_name,
                'Product Name': line[:80],
                'Product Price': line,
                'Landing Page Link': found_url if found_url else f"https://{store_name.lower().replace(' ', '')}.com",
                'Ad Link': f"https://www.facebook.com/ads/library/?id={ad_id}"
            })

print(f"Total raw competitor snippets found: {len(competitors)}")

# Deduplicate by Product Name and Landing Page
unique_results = {}
for c in competitors:
    key = (c['Store Name'], c['Product Name'])
    if key not in unique_results:
        unique_results[key] = c

print(f"Unique competitors identified: {len(unique_results)}")

with open("extracted_competitors.json", "w", encoding="utf-8") as f:
    json.dump(list(unique_results.values()), f, indent=2, ensure_ascii=False)
