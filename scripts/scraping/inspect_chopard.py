import os
import sys
import time
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

def inspect_chopard(url="https://www.chopard.com/en-intl/perfume-for-men/95201-0442.html"):
    print(f"Navigating to Chopard URL: {url}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url, wait_until='networkidle', timeout=30000)
        time.sleep(3)
        
        print(f"Page Title: {page.title()}")
        h1 = page.locator("h1").first
        if h1.is_visible():
            print(f"H1 Text: {h1.inner_text()}")

        imgs = page.eval_on_selector_all(
            "img",
            """elements => elements.map(e => e.src || e.getAttribute('data-src') || '').filter(s => s)"""
        )
        print(f"Found {len(imgs)} total DOM images.")
        for u in imgs:
            if any(k in u for k in ['ProductsAssets', '95201', '0442', 'perfume', 'product', 'Chopard', 'Malaki', 'Oud']):
                print("  [Product Image]:", u)

        browser.close()

if __name__ == '__main__':
    inspect_chopard()
