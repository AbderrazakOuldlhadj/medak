import os
import sys
import re
import json
import time
import io
import requests
from PIL import Image
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(os.path.join(ROOT_DIR, "scripts", "processing"))
from process_image_assets import format_image_to_square_webp

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
}

def sanitize_folder_name(name):
    clean = re.sub(r'[\\/*?:"<>|]', '', name).strip()
    return clean

def test_fetch_sephora(perfume_name):
    print(f"\n[Testing] Sephora FR for: '{perfume_name}'", flush=True)

    with sync_playwright() as p:
        user_data_dir = os.path.join(ROOT_DIR, "data", "interim", "sephora_playwright_profile")
        context = p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            viewport={"width": 1280, "height": 800},
            locale="fr-FR",
            args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
        )
        page = context.pages[0] if context.pages else context.new_page()

        # Clean query: brand + fragrance title without volume/concentration noise
        parts = perfume_name.split()
        brand = parts[0] if parts else ''
        name_clean = ' '.join([p for p in parts[1:] if p not in ['EDP', 'EDT', 'PARFUM', '100ML', '125ML', '200ML', '150ML', '75ML', '80ML', '90ML']])
        query_str = f"{brand} {name_clean}".strip()
        search_url = f"https://www.sephora.fr/recherche?q={query_str.replace(' ', '+')}"

        print(f"  Navigating to search: {search_url}", flush=True)
        page.goto(search_url, wait_until="domcontentloaded", timeout=25000)

        # Accept cookie banner if present
        try:
            cookie_btn = page.locator("#onetrust-accept-btn-handler")
            if cookie_btn.is_visible(timeout=3000):
                cookie_btn.click()
                print("  Accepted cookies.", flush=True)
        except Exception:
            pass

        time.sleep(3)

        # Find product links
        product_hrefs = page.eval_on_selector_all(
            "a[href*='/p/']",
            "elements => elements.map(e => e.href)"
        )

        print(f"  Found {len(product_hrefs)} product links.", flush=True)
        if not product_hrefs:
            context.close()
            return

        target_url = product_hrefs[0]
        print(f"  Opening product page: {target_url}", flush=True)
        page.goto(target_url, wait_until="domcontentloaded", timeout=25000)
        time.sleep(4)

        # Scroll page to trigger lazy loaded images
        page.evaluate("window.scrollTo(0, 500)")
        time.sleep(1)

        # Extract all media.sephora image URLs
        img_urls = page.eval_on_selector_all(
            "img[src*='media.sephora'], img[src*='demandware.static'], img[srcset*='media.sephora']",
            """elements => {
                const set = new Set();
                elements.forEach(e => {
                    if (e.src) set.add(e.src);
                    if (e.srcset) {
                        e.srcset.split(',').forEach(s => {
                            const u = s.trim().split(' ')[0];
                            if (u) set.add(u);
                        });
                    }
                });
                return Array.from(set);
            }"""
        )

        valid_product_imgs = []
        seen = set()
        for u in img_urls:
            if any(k in u for k in ['media_principal', 'media_', 'published', 'PIM', 'massivpimupload']):
                base = u.split('?')[0]
                if base not in seen:
                    seen.add(base)
                    high_res = f"{base}?scaleWidth=1000&scaleMode=fit"
                    valid_product_imgs.append(high_res)

        print(f"  Extracted {len(valid_product_imgs)} valid Sephora product images:", flush=True)
        for idx, u in enumerate(valid_product_imgs, start=1):
            print(f"    {idx}. {u}", flush=True)

        context.close()

if __name__ == '__main__':
    test_fetch_sephora("DIOR SAUVAGE EDT 100ML")
    test_fetch_sephora("AZZARO THE MOST WANTED EDP 100ML")
