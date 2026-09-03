import os
import sys
import re
import time
import requests
from bs4 import BeautifulSoup
from PIL import Image
from playwright.sync_api import sync_playwright

sys.path.append(os.path.join(r'c:\Users\msipc\Desktop\products\parfums', 'scripts', 'processing'))
from process_image_assets import format_image_to_square_webp

sys.stdout.reconfigure(encoding='utf-8')

def fetch_lacoste_noir():
    target_dir = r"c:\Users\msipc\Desktop\products\parfums\assets\product_images\LACOSTE L.12.12 NOIR 100ML"
    os.makedirs(target_dir, exist_ok=True)

    # Clean directory
    for f in os.listdir(target_dir):
        fp = os.path.join(target_dir, f)
        if os.path.isfile(fp):
            try: os.remove(fp)
            except Exception: pass

    url = 'https://www.notino.fr/lacoste/eau-de-lacoste-l-12-12-noir-eau-de-toilette-pour-homme/'

    candidate_urls = []
    print(f"Launching Playwright for Notino URL: {url}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=['--disable-blink-features=AutomationControlled'])
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
        page = context.new_page()

        try:
            page.goto(url, wait_until='domcontentloaded', timeout=25000)
            time.sleep(4)
        except Exception as e:
            print(f"Nav note: {e}")

        img_urls = page.eval_on_selector_all(
            'img, source',
            'elements => elements.map(e => e.src || e.srcset || e.getAttribute("data-src") || "").filter(s => s)'
        )

        for u in img_urls:
            for sub_u in u.split(','):
                raw_u = sub_u.strip().split(' ')[0]
                if not raw_u: continue
                c_lower = raw_u.lower()
                if any(x in c_lower for x in ['logo', 'icon', 'badge', 'flag', 'star', 'banner', 'avatar', 'footer', 'header', 'payment']):
                    continue
                if 'lacoste' in c_lower or 'notino' in c_lower or 'noir' in c_lower:
                    high_res = raw_u.replace('_thumb/', '_main_hq/').replace('_small/', '_main_hq/').replace('_lq/', '_hq/').replace('/thumb/', '/main_hq/').replace('/detail_main_lq/', '/detail_main_hq/')
                    if high_res not in candidate_urls:
                        candidate_urls.append(high_res)

        browser.close()

    print(f"Found {len(candidate_urls)} candidate Lacoste L.12.12 Noir photos:")
    for cu in candidate_urls:
        print("  ->", cu)

    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})

    saved = 0
    for idx, u in enumerate(candidate_urls, 1):
        try:
            r = session.get(u, timeout=12)
            if r.status_code == 200 and len(r.content) > 5000:
                ext = 'png' if u.lower().endswith('.png') else 'jpg'
                raw_name = f'raw_{saved+1}.{ext}'
                raw_path = os.path.join(target_dir, raw_name)
                with open(raw_path, 'wb') as f:
                    f.write(r.content)

                img = Image.open(raw_path)
                if img.width >= 200 and img.height >= 200:
                    webp_name = 'bottle.webp' if saved == 0 else f'image_{saved+1}.webp'
                    webp_path = os.path.join(target_dir, webp_name)
                    success = format_image_to_square_webp(img, webp_path, remove_bg=True)
                    if success:
                        print(f'  [✓ Saved Authentic Perfume Image {saved+1}] {raw_name} -> {webp_name} ({img.width}x{img.height}px, {len(r.content)//1024} KB)')
                        saved += 1
        except Exception as e:
            print(f'  Error {u}: {e}')

    print(f"Done! Successfully saved {saved} authentic Lacoste L.12.12 Noir EDT 100ml photos into LACOSTE L.12.12 NOIR 100ML/")

if __name__ == '__main__':
    fetch_lacoste_noir()
