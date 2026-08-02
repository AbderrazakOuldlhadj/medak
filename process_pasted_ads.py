import sys
import asyncio
import json
import re
import csv
import subprocess
import urllib.parse
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

CSV_PATH = "ads_research.csv"

def get_existing_ad_links():
    existing_links = set()
    existing_ids = set()
    try:
        with open(CSV_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                link = r.get("Ad Link", "").strip()
                if link:
                    existing_links.add(link)
                    id_match = re.search(r'id=(\d+)', link)
                    if id_match:
                        existing_ids.add(id_match.group(1))
    except Exception:
        pass
    return existing_links, existing_ids

def extract_price_from_text(text):
    matches = re.findall(r'(\b\d{1,3}(?:[.,\s]\d{3})*\s*(?:DZD|DA|د\.ج|دج)\b)', text, re.IGNORECASE)
    if matches:
        return matches[0].strip()
    
    raw_nums = re.findall(r'(\d{4,5})\s*(?:DZD|DA|دج)?', text)
    valid_nums = [n for n in raw_nums if int(n) >= 1000 and int(n) <= 50000]
    if valid_nums:
        return f"{int(valid_nums[0]):,} DZD".replace(",", " ")
    return "N/A"

def infer_gender(text_content):
    low = text_content.lower()
    if any(k in low for k in ["femme", "women", "her", "pour elle", "anti-chute", "soin", "beauty"]):
        return "Femme"
    elif any(k in low for k in ["homme", "men", "him", "pour homme", "man", "sauvage"]):
        return "Homme"
    return "Unisex"

async def process_single_ad_link(browser, ad_url):
    print(f"\nProcessing Ad Link: {ad_url}")
    ad_id_match = re.search(r'id=(\d+)', ad_url)
    ad_id = ad_id_match.group(1) if ad_id_match else "Unknown"

    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        locale="fr-FR"
    )
    
    # 1. Scrape Meta Ad Library Page
    page = await context.new_page()
    try:
        await page.goto(ad_url, wait_until="domcontentloaded", timeout=30000)
    except Exception as e:
        print("Ad load note:", e)

    await page.wait_for_timeout(6000)
    content = await page.content()
    soup = BeautifulSoup(content, 'html.parser')
    text = soup.get_text(separator="\n", strip=True)

    # Store Name
    store_name = "Algerian Store"
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    for i, line in enumerate(lines):
        if "Sponsorisé" in line or "Sponsored" in line:
            if i > 0:
                store_name = lines[i-1]
                break

    # Date Published
    date_pub = "Unknown"
    date_match = re.search(r'(Début de diffusion le|Started running on)\s+([^\n]+)', text)
    if date_match:
        date_pub = date_match.group(2).strip()

    # Product Name
    product_name = "Perfume Offer"
    for line in lines:
        if any(kw in line.lower() for kw in ["parfum", "pack", "coffret", "eau de", "fragrance", "armaf", "ysl", "dior", "boss", "givenchy", "cartier", "versace"]):
            if len(line) < 90:
                product_name = line
                break

    # Outbound Landing Page Link detection
    l_links = set(re.findall(r'l\.facebook\.com/l\.php\?u=([^&"\']+)', content))
    landing_url = ""
    for l in l_links:
        dec = urllib.parse.unquote(l)
        if not any(x in dec for x in ["facebook.com", "instagram.com", "alibaba.com", "doubleclick", "cnct.fr", "itunes.apple.com", "google.com", "m.me", "wa.me"]):
            landing_url = dec
            break

    # If no external landing page website, set Landing Page Link to "Message"
    if not landing_url or "m.me" in content or "wa.me" in content or "Send Message" in text or "Envoyer un message" in text:
        landing_url = "Message"

    # 2. Render Landing Page for Real Checkout Price (if external landing page exists)
    real_price = "N/A"
    if landing_url != "Message" and landing_url.startswith("http"):
        print(f"Rendering Landing Page for exact checkout price: {landing_url}")
        lp_page = await context.new_page()
        try:
            await lp_page.goto(landing_url, wait_until="networkidle", timeout=30000)
            await lp_page.wait_for_timeout(5000)
            lp_content = await lp_page.content()
            lp_soup = BeautifulSoup(lp_content, 'html.parser')
            lp_text = lp_soup.get_text(separator="\n", strip=True)
            
            real_price = extract_price_from_text(lp_text)
            print(f"Extracted Landing Page Price: {real_price}")
        except Exception as e:
            print("Landing page error:", e)
        finally:
            await lp_page.close()

    if real_price == "N/A":
        real_price = extract_price_from_text(text)

    gender = infer_gender(f"{product_name} {text}")
    await page.close()

    return {
        "Store Name": store_name,
        "Product Name": product_name,
        "Product Price": real_price,
        "Gender": gender,
        "Landing Page Link": landing_url,
        "Ad Link": ad_url,
        "Date Published": date_pub
    }

async def process_all(urls):
    existing_links, existing_ids = get_existing_ad_links()
    
    urls_to_scrape = []
    skipped_urls = []

    for u in urls:
        clean_u = u.strip()
        id_match = re.search(r'id=(\d+)', clean_u)
        ad_id = id_match.group(1) if id_match else None

        if clean_u in existing_links or (ad_id and ad_id in existing_ids):
            print(f"[SKIPPED] Duplicate Ad Link already exists in sheet: {clean_u}")
            skipped_urls.append(clean_u)
        else:
            urls_to_scrape.append(clean_u)

    if not urls_to_scrape:
        print("All pasted ad links already exist in ads_research.csv. No new entries added.")
        return []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        results = []
        for u in urls_to_scrape:
            if "facebook.com/ads/library" in u:
                rec = await process_single_ad_link(browser, u)
                results.append(rec)
        await browser.close()
        return results

def sync_csv(records):
    if not records:
        return
    fieldnames = ["Store Name", "Product Name", "Product Price", "Gender", "Landing Page Link", "Ad Link", "Date Published"]
    rows = []
    try:
        with open(CSV_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                rows.append(r)
    except Exception:
        pass

    for rec in records:
        rows.append(rec)

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"\nAppended {len(records)} new records to {CSV_PATH}.")
    
    # Sync git commit
    try:
        subprocess.run(f'git add "{CSV_PATH}" ; git commit -m "Auto-sync new unique ad links"', shell=True)
        print("Synced to git successfully.")
    except Exception as e:
        print("Git sync note:", e)

if __name__ == "__main__":
    urls_input = sys.argv[1:] if len(sys.argv) > 1 else []
    if not urls_input:
        raw_in = input("Paste Meta Ad Library URL(s): ")
        urls_input = re.findall(r'https?://[^\s]+', raw_in)

    if urls_input:
        recs = asyncio.run(process_all(urls_input))
        if recs:
            sync_csv(recs)
