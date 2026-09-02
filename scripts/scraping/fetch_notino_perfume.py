import os
import sys
import re
import time
import requests
from PIL import Image
from playwright.sync_api import sync_playwright

sys.path.append(os.path.join(r'c:\Users\msipc\Desktop\products\parfums', 'scripts', 'processing'))
from process_image_assets import format_image_to_square_webp

sys.stdout.reconfigure(encoding='utf-8')

def fetch_notino_perfume(url, target_folder_name):
    target_dir = os.path.join(r'c:\Users\msipc\Desktop\products\parfums\assets\product_images', target_folder_name)
    os.makedirs(target_dir, exist_ok=True)

    # Clean out folder first
    for f in os.listdir(target_dir):
        fp = os.path.join(target_dir, f)
        if os.path.isfile(fp):
            try: os.remove(fp)
            except Exception: pass

    print(f"Launching Playwright for Notino URL: {url}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=['--disable-blink-features=AutomationControlled'])
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
        page = context.new_page()

        try:
            page.goto(url, wait_until='networkidle', timeout=25000)
        except Exception as e:
            print(f"Navigation note: {e}")

        time.sleep(4)

        print(f"Page Title: {page.title()}")
        print(f"Page URL: {page.url}")

        # Extract all img elements and picture sources
        imgs = page.eval_on_selector_all(
            'img, source',
            'elements => elements.map(e => e.src || e.srcset || e.getAttribute("data-src") || e.getAttribute("data-srcset") || "").filter(s => s)'
        )

        candidate_urls = []
        for u in imgs:
            # Handle srcset split by space/comma
            for sub_u in u.split(','):
                clean_u = sub_u.strip().split(' ')[0]
                c_lower = clean_u.lower()
                if any(x in c_lower for x in ['logo', 'icon', 'badge', 'flag', 'star', 'banner', 'avatar', 'footer', 'header', 'payment', 'facebook', 'instagram', 'youtube', 'gallery/ba/']):
                    continue
                if any(ext in c_lower for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                    high_res = clean_u.replace('_thumb/', '_main_hq/').replace('_small/', '_main_hq/').replace('_lq/', '_hq/').replace('/thumb/', '/main_hq/').replace('/detail_main_lq/', '/detail_main_hq/')
                    if high_res not in candidate_urls:
                        candidate_urls.append(high_res)

        print(f"Found {len(candidate_urls)} authentic Notino perfume candidate photos:")
        for cu in candidate_urls:
            print("  ->", cu)

        saved = 0
        for idx, u in enumerate(candidate_urls, 1):
            try:
                res = page.request.get(u)
                if res.status == 200 and len(res.body()) > 5000:
                    ext = 'png' if u.lower().endswith('.png') else 'jpg'
                    raw_name = f'raw_{saved+1}.{ext}'
                    raw_path = os.path.join(target_dir, raw_name)
                    with open(raw_path, 'wb') as f:
                        f.write(res.body())

                    img = Image.open(raw_path)
                    if img.width >= 200 and img.height >= 200:
                        webp_name = 'bottle.webp' if saved == 0 else f'image_{saved+1}.webp'
                        webp_path = os.path.join(target_dir, webp_name)
                        success = format_image_to_square_webp(img, webp_path, remove_bg=True)
                        if success:
                            print(f'  [✓ Saved Authentic Perfume Image {saved+1}] {raw_name} -> {webp_name} ({img.width}x{img.height}px, {len(res.body())//1024} KB)')
                            saved += 1
            except Exception as e:
                print(f'  Error {u}: {e}')

        browser.close()

    print(f"Done! Successfully saved {saved} authentic perfume photos into {target_folder_name}/")
    return saved

if __name__ == '__main__':
    url = sys.argv[1] if len(sys.argv) > 1 else 'https://www.notino.fr/guerlain/absolus-allegoria-santal-royal-eau-de-parfum-mixte/'
    folder = sys.argv[2] if len(sys.argv) > 2 else 'ABSOLUS ALLEGORIA SANTAL ROYAL 125ML'
    fetch_notino_perfume(url, folder)
