import asyncio
import json
import urllib.parse
import re
import csv
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

SEARCH_TERMS = [
    "parfum dior dz",
    "parfum lattafa dz",
    "parfum armaf algerie",
    "عطور رجال الجزائر",
    "عطر اصلي الجزائر",
    "parfum Givenchy dz"
]
COUNTRY = "DZ"

async def deep_search():
    extracted_data = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            locale="fr-FR"
        )
        
        for term in SEARCH_TERMS:
            encoded_q = urllib.parse.quote(term)
            search_url = f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country={COUNTRY}&q={encoded_q}&search_type=keyword_unordered&media_type=all"
            print(f"Deep Search for: '{term}'...")

            page = await context.new_page()
            try:
                await page.goto(search_url, wait_until="domcontentloaded", timeout=25000)
            except Exception as e:
                print(f"Goto note for '{term}':", e)

            await page.wait_for_timeout(6000)

            # Scroll multiple times
            for _ in range(5):
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(2500)

            content = await page.content()
            await page.close()

            # Save HTML dump
            file_key = term.replace(" ", "_").replace("ع", "a").replace("ط", "t").replace("و", "w").replace("ر", "r")
            with open(f"more_{file_key}.html", "w", encoding="utf-8") as f:
                f.write(content)

            print(f"Finished search for {term}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(deep_search())
