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

def fetch_clinique_playwright():
    target_dir = r'c:\Users\msipc\Desktop\products\parfums\assets\product_images\CLINIQUE HAPPY COLOGNE FOR MEN EDT 100ML'
    os.makedirs(target_dir, exist_ok=True)

    # Clean out old bad files
    for f in os.listdir(target_dir):
        fp = os.path.join(target_dir, f)
        if os.path.isfile(fp):
            try: os.remove(fp)
            except Exception: pass

    url = 'https://www.clinique.com/product/1617/5190/mens/cologne/clinique-happy-for-men/clinique-happy-for-men-cologne-spray?size=3.4_fl.oz._%2F_100ml'

    print("Launching Playwright to inspect Clinique URL...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
        page = context.new_page()
        page.goto(url, wait_until='domcontentloaded', timeout=30000)
        time.sleep(4)

        print(f"Page Title: {page.title()}")

        imgs = page.eval_on_selector_all(
            "img",
            "elements => elements.map(e => e.src || e.getAttribute('data-src') || '').filter(s => s)"
        )
        browser.close()

    print(f"Found {len(imgs)} total DOM images.")
    candidate_urls = []
    for u in imgs:
        u_lower = u.lower()
        if any(x in u_lower for x in ['logo', 'icon', 'bag', 'star', 'banner', 'avatar', 'footer', 'header', 'social', 'flag']):
            continue
        if any(x in u_lower for x in ['clinique', 'scene7', 'elcassets', 'is/image', 'product', '5190', 'happy']):
            # Convert Scene7 thumbnail params to high resolution
            high_res = re.sub(r'wid=\d+', 'wid=1500', u)
            high_res = re.sub(r'hei=\d+', 'hei=1500', high_res)
            if high_res not in candidate_urls:
                candidate_urls.append(high_res)

    print(f"Filter yielded {len(candidate_urls)} candidate high-res URLs:")
    for cu in candidate_urls:
        print("  ->", cu)

    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})

    saved = 0
    for idx, u in enumerate(candidate_urls, 1):
        try:
            r = session.get(u, timeout=12)
            if r.status_code == 200 and len(r.content) > 5000:
                ext = 'png' if u.lower().endswith('.png') else 'jpg'
                raw_name = f'raw_{idx}.{ext}'
                raw_path = os.path.join(target_dir, raw_name)
                with open(raw_path, 'wb') as f:
                    f.write(r.content)
                
                img = Image.open(raw_path)
                webp_name = 'bottle.webp' if idx == 1 else f'image_{idx}.webp'
                webp_path = os.path.join(target_dir, webp_name)
                
                success = format_image_to_square_webp(img, webp_path, remove_bg=True)
                if success:
                    print(f'  [✓ Saved Authentic Image {idx}] {raw_name} -> {webp_name} ({img.width}x{img.height}px, {len(r.content)//1024} KB)')
                    saved += 1
        except Exception as e:
            print(f'  Error downloading {u}: {e}')

    print(f"Done! Successfully saved {saved} authentic Clinique Happy product images into CLINIQUE HAPPY COLOGNE FOR MEN EDT 100ML/")

if __name__ == '__main__':
    fetch_clinique_playwright()
