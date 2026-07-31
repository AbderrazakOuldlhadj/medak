import asyncio
import json
import urllib.parse
import re
import csv
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

KEYWORDS = [
    "parfum original dz",
    "pack parfum",
    "parfum homme",
    "parfumerie dz"
]
COUNTRY = "DZ"

async def run_market_search():
    found_competitors = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            locale="fr-FR"
        )
        
        for kw in KEYWORDS:
            encoded_q = urllib.parse.quote(kw)
            search_url = f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country={COUNTRY}&q={encoded_q}&search_type=keyword_unordered&media_type=all"
            print(f"Searching Meta Ads for: '{kw}' in Algeria...")
            
            page = await context.new_page()
            try:
                await page.goto(search_url, wait_until="domcontentloaded", timeout=25000)
            except Exception as e:
                print(f"Goto warning for {kw}:", e)

            await page.wait_for_timeout(6000)
            
            # Scroll down to load ad cards
            for _ in range(4):
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(2500)

            content = await page.content()
            await page.close()

            soup = BeautifulSoup(content, 'html.parser')
            
            # Save raw html dump
            with open(f"search_{kw.replace(' ', '_')}.html", "w", encoding="utf-8") as f:
                f.write(content)

            # Find all redirect landing pages
            l_links = set(re.findall(r'l\.facebook\.com/l\.php\?u=([^&"\']+)', content))
            ad_ids = re.findall(r'id=(\d{10,})', content)

            print(f"Found {len(l_links)} landing page links and {len(ad_ids)} ad IDs for '{kw}'")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_market_search())
