import asyncio
import json
import re
import urllib.parse
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

AD_URL = "https://www.facebook.com/ads/library/?id=1701177097798374"

async def scrape_ad():
    print(f"Scraping Ad: {AD_URL}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            locale="fr-FR"
        )
        page = await context.new_page()

        try:
            await page.goto(AD_URL, wait_until="domcontentloaded", timeout=30000)
        except Exception as e:
            print("Page goto note:", e)

        await page.wait_for_timeout(6000)

        content = await page.content()
        await browser.close()

        with open("ad_1701177097798374.html", "w", encoding="utf-8") as f:
            f.write(content)

        soup = BeautifulSoup(content, 'html.parser')
        text = soup.get_text(separator="\n", strip=True)

        with open("ad_1701177097798374.txt", "w", encoding="utf-8") as f:
            f.write(text)

        # Extract l.facebook links
        l_links = set(re.findall(r'l\.facebook\.com/l\.php\?u=([^&"\']+)', content))
        clean_links = [urllib.parse.unquote(l) for l in l_links if not any(x in l for x in ["facebook.com", "instagram.com", "alibaba.com", "doubleclick", "cnct.fr", "itunes.apple.com", "google.com"])]

        print("Extracted text preview:")
        print(text[:1500])
        print("\nExtracted clean destination URLs:")
        for link in clean_links:
            print("-", link)

if __name__ == "__main__":
    asyncio.run(scrape_ad())
