import asyncio
import json
import re
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def scrape_meta_ad(ad_url):
    print(f"Navigating to: {ad_url}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            locale="en-US"
        )
        page = await context.new_page()
        
        # Intercept requests to capture potential GraphQL or API responses
        captured_links = []
        def handle_request(request):
            url = request.url
            if "l.facebook.com" in url or "http" in url:
                pass

        page.on("request", handle_request)
        
        try:
            await page.goto(ad_url, wait_until="networkidle", timeout=30000)
        except Exception as e:
            print("Goto timeout or error, proceeding to parse content...", e)
            
        await page.wait_for_timeout(5000)
        
        content = await page.content()
        await browser.close()
        
        with open("scraped_ad.html", "w", encoding="utf-8") as f:
            f.write(content)
            
        soup = BeautifulSoup(content, 'html.parser')
        
        text_content = soup.get_text(separator="\n", strip=True)
        with open("scraped_text.txt", "w", encoding="utf-8") as f:
            f.write(text_content)
            
        print("Page dumped successfully.")
        
        # Look for links
        links = []
        for a in soup.find_all('a', href=True):
            links.append(a['href'])
        
        with open("scraped_links.json", "w", encoding="utf-8") as f:
            json.dump(links, f, indent=2)

if __name__ == "__main__":
    asyncio.run(scrape_meta_ad("https://www.facebook.com/ads/library/?id=1266422528876738"))
