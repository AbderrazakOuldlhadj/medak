import asyncio
import json
import urllib.parse
import re
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

KEYWORDS = ["parfum", "parfumerie", "coffret parfum", "parfum original"]
COUNTRY = "DZ"

async def search_and_extract(keyword):
    encoded_q = urllib.parse.quote(keyword)
    search_url = f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country={COUNTRY}&q={encoded_q}&search_type=keyword_unordered&media_type=all"
    print(f"Opening Meta Ads Library for: '{keyword}'...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            locale="fr-FR"
        )
        page = await context.new_page()

        try:
            await page.goto(search_url, wait_until="domcontentloaded", timeout=20000)
        except Exception as e:
            print("Goto warning:", e)

        # Wait for ad cards container
        await page.wait_for_timeout(8000)

        # Scroll to load more ads
        for _ in range(3):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(3000)

        content = await page.content()
        await browser.close()

        soup = BeautifulSoup(content, 'html.parser')
        
        # Save HTML
        filename = f"search_{keyword.replace(' ', '_')}.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Saved {filename}")

        # Extract text blocks
        text_content = soup.get_text(separator="\n", strip=True)
        with open(f"text_{keyword.replace(' ', '_')}.txt", "w", encoding="utf-8") as f:
            f.write(text_content)

        # Extract links
        links = [a['href'] for a in soup.find_all('a', href=True)]
        with open(f"links_{keyword.replace(' ', '_')}.json", "w", encoding="utf-8") as f:
            json.dump(links, f, indent=2)

if __name__ == "__main__":
    asyncio.run(search_and_extract("parfum"))
