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

def get_sephora_images_for_perfume(page, perfume_name):
    parts = perfume_name.split()
    brand = parts[0] if parts else ''
    name_clean = ' '.join([p for p in parts[1:] if p.upper() not in ['EDP', 'EDT', 'PARFUM', '100ML', '125ML', '200ML', '150ML', '75ML', '80ML', '90ML', '100', 'ML']])
    query_str = f"{brand} {name_clean}".strip()
    search_url = f"https://www.sephora.fr/recherche?q={query_str.replace(' ', '+')}"

    print(f"\n  Search URL: {search_url}", flush=True)

    try:
        page.goto(search_url, wait_until="domcontentloaded", timeout=25000)
    except Exception as e:
        print(f"  [Warning] Timeout navigating search: {e}", flush=True)

    # Remove privacy overlay banner that intercepts pointer events
    try:
        page.evaluate("""() => {
            ['#tc-privacy-wrapper', '#tc-privacy-overlay-banner', '#onetrust-consent-sdk'].forEach(id => {
                const el = document.querySelector(id);
                if (el) el.remove();
            });
        }""")
    except Exception:
        pass

    time.sleep(2)

    # Find product link
    product_link = page.locator("a[href*='/p/']").first

    if not product_link.is_visible():
        # Fallback query: Brand + first 2 words
        if len(parts) >= 2:
            query_fb = f"{parts[0]} {parts[1]}"
            search_url_fb = f"https://www.sephora.fr/recherche?q={query_fb.replace(' ', '+')}"
            try:
                page.goto(search_url_fb, wait_until="domcontentloaded", timeout=20000)
                time.sleep(2)
                page.evaluate("""() => {
                    ['#tc-privacy-wrapper', '#tc-privacy-overlay-banner', '#onetrust-consent-sdk'].forEach(id => {
                        const el = document.querySelector(id);
                        if (el) el.remove();
                    });
                }""")
                product_link = page.locator("a[href*='/p/']").first
            except Exception:
                pass

    if not product_link.is_visible():
        print(f"  ✗ No Sephora FR product link found for '{perfume_name}'", flush=True)
        return []

    try:
        print("  → Clicking product link...", flush=True)
        product_link.click(force=True)
        time.sleep(4)
        page.evaluate("window.scrollTo(0, 500)")
        time.sleep(2)
    except Exception as e:
        print(f"  [Warning] Product click error: {e}", flush=True)

    # Extract all media.sephora.eu / demandware product images
    all_imgs = page.eval_on_selector_all(
        "img, source",
        """elements => {
            const set = new Set();
            elements.forEach(e => {
                const s = e.src || e.getAttribute('data-src') || '';
                if (s) set.add(s);
                const srcset = e.srcset || e.getAttribute('data-srcset') || '';
                if (srcset) {
                    srcset.split(',').forEach(item => {
                        const url = item.trim().split(' ')[0];
                        if (url) set.add(url);
                    });
                }
            });
            return Array.from(set);
        }"""
    )

    valid_urls = []
    seen_bases = set()

    for u in all_imgs:
        if ('media.sephora.eu' in u or 'demandware.static' in u) and any(k in u for k in ['media_principal', 'media_', 'published', 'PIM', 'massivpimupload']):
            base_url = u.split('?')[0]
            if base_url not in seen_bases:
                seen_bases.add(base_url)
                # Request 1000px high-res version from Sephora media CDN
                high_res_url = f"{base_url}?scaleWidth=1000&scaleMode=fit"
                valid_urls.append(high_res_url)

    print(f"  ✓ Extracted {len(valid_urls)} Sephora FR product images.", flush=True)
    return valid_urls

def process_sephora_images_for_perfumes():
    target_json = os.path.join(ROOT_DIR, "data", "interim", "target_perfumes_from_sheet.json")
    if not os.path.exists(target_json):
        print(f"Error: {target_json} not found.")
        return

    with open(target_json, "r", encoding="utf-8") as f:
        perfumes = json.load(f)

    total = len(perfumes)
    print(f"Starting Sephora FR Product Image Extraction Pipeline for {total} perfumes...", flush=True)

    profile_id = int(time.time())
    user_data_dir = os.path.join(ROOT_DIR, "data", "interim", f"sephora_profile_{profile_id}")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            viewport={"width": 1280, "height": 800},
            locale="fr-FR",
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-setuid-sandbox'
            ]
        )

        completed = 0

        for i, item in enumerate(perfumes, start=1):
            full_name = item['full_name']
            folder_name = sanitize_folder_name(full_name)
            perfume_dir = os.path.join(ROOT_DIR, "assets", "product_images", folder_name)
            os.makedirs(perfume_dir, exist_ok=True)

            print(f"\n[{i}/{total}] Processing: {full_name}", flush=True)
            page = context.new_page()

            # Clear out previous legacy images (bottle.webp, package.webp, both.webp)
            for old_f in ['bottle.webp', 'package.webp', 'both.webp']:
                old_p = os.path.join(perfume_dir, old_f)
                if os.path.exists(old_p):
                    try:
                        os.remove(old_p)
                    except Exception:
                        pass

            # Extract Sephora FR product image URLs
            urls = get_sephora_images_for_perfume(page, full_name)
            page.close()

            if not urls:
                print(f"  ✗ No Sephora FR images retrieved for {full_name}", flush=True)
                continue

            # Download and save images as 1.webp, 2.webp, 3.webp...
            saved_count = 0
            for idx, img_url in enumerate(urls, start=1):
                out_path = os.path.join(perfume_dir, f"{idx}.webp")
                try:
                    res = requests.get(img_url, headers=HEADERS, timeout=12)
                    if res.status_code == 200 and len(res.content) > 3000:
                        img = Image.open(io.BytesIO(res.content))
                        success = format_image_to_square_webp(img, out_path, remove_bg=False)
                        if success:
                            saved_count += 1
                            print(f"    Saved: {idx}.webp from Sephora FR", flush=True)
                except Exception as e:
                    print(f"    [Error downloading {img_url}]: {e}", flush=True)

            if saved_count > 0:
                completed += 1

            time.sleep(0.5)

        context.close()

    print("\n" + "="*70, flush=True)
    print(f"Sephora FR Pipeline Complete! Successfully fetched images for {completed}/{total} perfumes.", flush=True)
    print("All images stored in ./assets/product_images/{PerfumeName}/[1.webp, 2.webp, ...]", flush=True)
    print("="*70, flush=True)

if __name__ == '__main__':
    process_sephora_images_for_perfumes()
