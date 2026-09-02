import sys
import json
import time
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

def test_sephora_playwright(search_query):
    with sync_playwright() as p:
        print(f"Launching Playwright browser for '{search_query}'...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            locale="fr-FR"
        )
        page = context.new_page()

        # Navigate to Sephora FR search page
        search_url = f"https://www.sephora.fr/recherche?q={search_query.replace(' ', '+')}"
        print(f"Navigating to: {search_url}")
        page.goto(search_url, wait_until="domcontentloaded", timeout=30000)

        # Accept cookies if cookie banner appears
        try:
            cookie_btn = page.locator("#onetrust-accept-btn-handler")
            if cookie_btn.is_visible(timeout=3000):
                cookie_btn.click()
                print("Accepted cookie banner.")
        except Exception:
            pass

        time.sleep(2)

        # Find first product link
        product_links = page.locator("a.product-tile-link, a.product-tile, div.product-tile a").all()
        print(f"Found {len(product_links)} product tile links.")

        if not product_links:
            # Fallback: get any href containing /p/
            hrefs = page.eval_on_selector_all("a[href*='/p/']", "elements => elements.map(e => e.href)")
            print(f"Found {len(hrefs)} /p/ hrefs.")
            if hrefs:
                target_url = hrefs[0]
            else:
                print("No product link found.")
                browser.close()
                return []
        else:
            target_url = product_links[0].get_attribute("href")
            if target_url and not target_url.startswith("http"):
                target_url = "https://www.sephora.fr" + target_url

        print(f"Opening Product Page: {target_url}")
        page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(2)

        # Extract all product image URLs (from srcset, img src, or Sephora hi-res image attributes)
        img_urls = page.eval_on_selector_all(
            "img[src*='demandware.static'], img[src*='products_all'], img[srcset*='demandware.static']",
            """elements => {
                const urls = new Set();
                elements.forEach(e => {
                    if (e.src) urls.add(e.src);
                    if (e.srcset) {
                        e.srcset.split(',').forEach(s => {
                            const u = s.trim().split(' ')[0];
                            if (u) urls.add(u);
                        });
                    }
                });
                return Array.from(urls);
            }"""
        )

        print(f"Extracted {len(img_urls)} product image URLs:")
        for u in img_urls:
            print("  ", u)

        browser.close()
        return img_urls

if __name__ == '__main__':
    test_sephora_playwright("Dior Sauvage Eau de Toilette")
