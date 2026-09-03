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

def fetch_jpg_scandal():
    target_dir = r"c:\Users\msipc\Desktop\products\parfums\assets\product_images\JEAN PAUL GAULTIER SCANDALE PARFUM 150ML"
    os.makedirs(target_dir, exist_ok=True)

    urls = [
        'https://www.notino.fr/jean-paul-gaultier/scandal-pour-homme-le-parfum-eau-de-parfum-rechargeable-pour-homme/',
        'https://odorem-dz.com/produit/scandal-pour-homme-le-parfum-100ml/'
    ]

    candidate_urls = []

    print("Launching Playwright for Notino Scandal Pour Homme Le Parfum...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=['--disable-blink-features=AutomationControlled'])
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        page = context.new_page()

        try:
            page.goto(urls[0], wait_until='domcontentloaded', timeout=30000)
            time.sleep(3)
        except Exception as e:
            print(f"Nav note: {e}")

        img_urls = page.eval_on_selector_all(
            'img, source',
            'elements => elements.map(e => e.src || e.srcset || e.getAttribute("data-src") || "").filter(s => s)'
        )

        for u in img_urls:
            for sub_u in u.split(','):
                clean_u = sub_u.strip().split(' ')[0]
                c_lower = clean_u.lower()
                if any(x in c_lower for x in ['logo', 'icon', 'badge', 'flag', 'star', 'banner', 'avatar', 'footer', 'header', 'payment', 'facebook', 'instagram', 'youtube', 'gallery/ba/']):
                    continue
                if any(ext in c_lower for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                    high_res = clean_u.replace('_thumb/', '_main_hq/').replace('_small/', '_main_hq/').replace('_lq/', '_hq/').replace('/thumb/', '/main_hq/').replace('/detail_main_lq/', '/detail_main_hq/')
                    if high_res not in candidate_urls:
                        candidate_urls.append(high_res)

        browser.close()

    # Search Odorem DZ as well
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
    try:
        od_res = session.get(urls[1], timeout=12)
        if od_res.status_code == 200:
            soup = BeautifulSoup(od_res.text, 'html.parser')
            gallery = soup.find_all(class_=re.compile(r'woocommerce-product-gallery|product-gallery|gallery', re.I))
            for g in gallery:
                for ga in g.find_all('a', href=True):
                    if any(ext in ga['href'].lower() for ext in ['.jpg', '.png', '.webp']):
                        u_clean = re.sub(r'-\d+x\d+(\.[a-zA-Z0-9]+)$', r'\1', ga['href'])
                        if u_clean not in candidate_urls:
                            candidate_urls.append(u_clean)
                for img in g.find_all('img'):
                    val = img.get('data-large_image') or img.get('src') or img.get('data-src')
                    if val and any(ext in val.lower() for ext in ['.jpg', '.png', '.webp']):
                        u_clean = re.sub(r'-\d+x\d+(\.[a-zA-Z0-9]+)$', r'\1', val)
                        if u_clean not in candidate_urls:
                            candidate_urls.append(u_clean)
    except Exception as e:
        print(f"Odorem DZ note: {e}")

    print(f"Found {len(candidate_urls)} candidate JPG Scandal Pour Homme Le Parfum photos:")
    for cu in candidate_urls:
        print("  ->", cu)

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

    print(f"Done! Successfully saved {saved} authentic JPG Scandal Pour Homme Le Parfum photos into JEAN PAUL GAULTIER SCANDALE PARFUM 150ML/")

if __name__ == '__main__':
    fetch_jpg_scandal()
