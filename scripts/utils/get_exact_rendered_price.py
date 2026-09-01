import asyncio
import re
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

URL = "https://pafen-dz.com/order/4223-pack-promo-club-de-nuit"

async def get_rendered_price():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            locale="fr-FR"
        )
        page = await context.new_page()

        print(f"Opening landing page: {URL}")
        try:
            await page.goto(URL, wait_until="networkidle", timeout=30000)
        except Exception as e:
            print("Goto note:", e)

        await page.wait_for_timeout(6000)

        content = await page.content()
        await browser.close()

        soup = BeautifulSoup(content, 'html.parser')
        text = soup.get_text(separator="\n", strip=True)

        with open("rendered_pafen.txt", "w", encoding="utf-8") as f:
            f.write(text)

        print("\nRendered text preview:")
        lines = [line for line in text.split("\n") if line.strip()]
        for i, line in enumerate(lines[:100]):
            print(f"{i}: {line}")

if __name__ == "__main__":
    asyncio.run(get_rendered_price())
