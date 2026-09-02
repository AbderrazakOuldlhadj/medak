import os
import sys
import time
import requests
from PIL import Image
from playwright.sync_api import sync_playwright

sys.path.append(os.path.join(r'c:\Users\msipc\Desktop\products\parfums', 'scripts', 'processing'))
from process_image_assets import format_image_to_square_webp

sys.stdout.reconfigure(encoding='utf-8')

def fetch_dior_sauvage_official():
    target_dir = r'c:\Users\msipc\Desktop\products\parfums\assets\product_images\DIOR SAUVAGE EDT 100ML'
    os.makedirs(target_dir, exist_ok=True)

    # Clean directory
    for f in os.listdir(target_dir):
        fp = os.path.join(target_dir, f)
        if os.path.isfile(fp):
            try: os.remove(fp)
            except Exception: pass

    url = 'https://www.dior.com/en_int/beauty/products/sauvage-eau-de-toilette-Y0685240.html'

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=['--disable-blink-features=AutomationControlled'])
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
        page = context.new_page()

        print("Navigating to official Dior Sauvage Y0685240 page...")
        page.goto(url, wait_until='domcontentloaded', timeout=25000)
        time.sleep(4)

        img_urls = page.eval_on_selector_all(
            'img',
            'elements => elements.map(e => e.src || e.getAttribute("data-src") || "").filter(s => s)'
        )

        candidate_urls = []
        for u in img_urls:
            u_lower = u.lower()
            if any(x in u_lower for x in ['logo', 'icon', 'bag', 'star', 'banner', 'avatar', 'footer', 'header', 'social', 'flag']):
                continue
            if 'Y0685240' in u or 'sauvage' in u_lower or 'demandware.static' in u_lower:
                if u not in candidate_urls:
                    candidate_urls.append(u)

        print(f"Extracted {len(candidate_urls)} candidate product URLs:")
        for cu in candidate_urls:
            print("  ->", cu)

        saved = 0
        for idx, u in enumerate(candidate_urls[:6], 1):
            try:
                res = page.request.get(u)
                if res.status == 200 and len(res.body()) > 5000:
                    raw_name = f'raw_{idx}.jpg'
                    raw_path = os.path.join(target_dir, raw_name)
                    with open(raw_path, 'wb') as f:
                        f.write(res.body())

                    img = Image.open(raw_path)
                    webp_name = 'bottle.webp' if idx == 1 else f'image_{idx}.webp'
                    webp_path = os.path.join(target_dir, webp_name)
                    success = format_image_to_square_webp(img, webp_path, remove_bg=True)
                    if success:
                        print(f'  [✓ Downloaded & Processed] {raw_name} -> {webp_name} ({img.width}x{img.height}px, {len(res.body())//1024} KB)')
                        saved += 1
            except Exception as e:
                print(f'  Error {u}: {e}')

        browser.close()

    print(f"Done! Successfully saved {saved} authentic Dior Sauvage Y0685240 photos into DIOR SAUVAGE EDT 100ML/")

if __name__ == '__main__':
    fetch_dior_sauvage_official()
