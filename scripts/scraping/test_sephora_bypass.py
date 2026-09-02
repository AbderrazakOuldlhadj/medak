import os
import sys
import time
from PIL import Image
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(os.path.join(ROOT_DIR, "scripts", "processing"))
from process_image_assets import format_image_to_square_webp

def download_sephora_images(product_name="AZZARO WANTED BY NIGHT EDP 100ML"):
    perfume_dir = os.path.join(ROOT_DIR, "assets", "product_images", product_name)
    os.makedirs(perfume_dir, exist_ok=True)
    
    clean_query = "azzaro wanted by night"
    search_url = f"https://www.sephora.fr/recherche?q={clean_query.replace(' ', '+')}"
    user_data_dir = os.path.join(ROOT_DIR, "data", "interim", "sephora_test_profile")

    print(f"Navigating via Sephora Search: {search_url}")

    captured_urls = []

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            viewport={'width': 1280, 'height': 800},
            locale='fr-FR',
            args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
        )
        page = context.new_page()

        page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
        time.sleep(3)

        # Clear cookie banner
        page.evaluate("""() => {
            ['#tc-privacy-wrapper', '#tc-privacy-overlay-banner', '#onetrust-consent-sdk'].forEach(id => {
                const el = document.querySelector(id);
                if (el) el.remove();
            });
        }""")

        product_link = page.locator("a[href*='/p/']").first
        if product_link.is_visible():
            print("Found Sephora product link! Clicking...")
            product_link.click(force=True)
            time.sleep(4)
            page.evaluate("window.scrollTo(0, 600)")
            time.sleep(2)

        # Extract img src from DOM
        all_imgs = page.eval_on_selector_all(
            "img, source",
            """elements => {
                const set = new Set();
                elements.forEach(e => {
                    const s = e.src || e.getAttribute('data-src') || '';
                    if (s) set.add(s);
                });
                return Array.from(set);
            }"""
        )

        seen = set()
        for u in all_imgs:
            if any(k in u for k in ['media.sephora.eu', 'demandware.static']) and any(k in u for k in ['media_principal', 'media_', 'published', 'PIM', 'massivpimupload']):
                base_u = u.split('?')[0]
                high_res = f"{base_u}?scaleWidth=1000&scaleMode=fit"
                if high_res not in seen:
                    seen.add(high_res)
                    captured_urls.append(high_res)

        print(f"\nExtracted {len(captured_urls)} REAL Sephora product image URLs.")

        # Wipe old files from directory
        for f in os.listdir(perfume_dir):
            fp = os.path.join(perfume_dir, f)
            if os.path.isfile(fp):
                try: os.remove(fp)
                except Exception: pass

        downloaded_files = []
        idx = 1

        # Download directly inside Playwright context to bypass CDN 403 blocks
        for img_url in captured_urls:
            try:
                response = page.request.get(img_url)
                if response.status == 200 and len(response.body()) > 5000:
                    raw_name = f"raw_{idx}.jpg"
                    raw_path = os.path.join(perfume_dir, raw_name)
                    
                    with open(raw_path, 'wb') as f:
                        f.write(response.body())
                    
                    img = Image.open(raw_path)
                    webp_name = "bottle.webp" if idx == 1 else f"image_{idx}.webp"
                    webp_path = os.path.join(perfume_dir, webp_name)
                    
                    success = format_image_to_square_webp(img, webp_path, remove_bg=True)
                    if success:
                        print(f"  [✓ Real Sephora Image {idx}] Saved {raw_name} -> {webp_name} ({img.width}x{img.height}px, {len(response.body())//1024} KB)")
                        downloaded_files.append(webp_path)
                    idx += 1
            except Exception as e:
                print(f"  [Download Error for {img_url}]: {e}")

        context.close()

    print(f"\nSuccessfully downloaded {len(downloaded_files)} authentic Sephora product images into:")
    print(perfume_dir)
    return downloaded_files

if __name__ == '__main__':
    download_sephora_images()
