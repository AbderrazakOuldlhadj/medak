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

def fetch_guerlain_extreme():
    target_dir = r"c:\Users\msipc\Desktop\products\parfums\assets\product_images\GUERLAIN L'HOMME IDEAL EXTREME EDP 100ML"
    os.makedirs(target_dir, exist_ok=True)

    url = 'https://www.guerlain.com/fr/fr-fr/p/lhomme-ideal-de-guerlain-paris-extreme---eau-de-parfum-P030435.html'

    print(f"Launching Playwright for Guerlain official URL: {url}")
    candidate_urls = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=['--disable-blink-features=AutomationControlled'])
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
        page = context.new_page()

        try:
            page.goto(url, wait_until='domcontentloaded', timeout=30000)
            time.sleep(4)
        except Exception as e:
            print(f"Nav note: {e}")

        # Accept cookie banner if present
        for selector in ['#onetrust-accept-btn-handler', 'button:has-text("Tout accepter")', 'button:has-text("Accepter")']:
            try:
                btn = page.locator(selector).first
                if btn.is_visible():
                    btn.click()
                    time.sleep(1)
                    break
            except Exception:
                pass

        img_urls = page.eval_on_selector_all(
            'img, source',
            'elements => elements.map(e => e.src || e.srcset || e.getAttribute("data-src") || "").filter(s => s)'
        )

        for u in img_urls:
            for sub_u in u.split(','):
                raw_u = sub_u.strip().split(' ')[0]
                if not raw_u: continue
                c_lower = raw_u.lower()
                if any(x in c_lower for x in ['logo', 'icon', 'badge', 'flag', 'star', 'banner', 'avatar', 'footer', 'header', 'payment', 'facebook', 'instagram', 'youtube']):
                    continue
                if '030435' in raw_u or 'ideal' in c_lower or 'demandware.static' in c_lower or 'guerlain' in c_lower:
                    high_res = re.sub(r'sw=\d+', 'sw=1500', raw_u)
                    high_res = re.sub(r'sh=\d+', 'sh=1500', high_res)
                    if high_res not in candidate_urls:
                        candidate_urls.append(high_res)

        browser.close()

    # Also search Odorem DZ for Guerlain L'Homme Ideal Extreme
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
    try:
        od_res = session.get('https://odorem-dz.com/?s=ideal+extreme&post_type=product', timeout=12)
        if od_res.status_code == 200:
            soup = BeautifulSoup(od_res.text, 'html.parser')
            for a in soup.find_all('a', href=True):
                if '/produit/' in a['href'] and 'extreme' in a['href'].lower():
                    p_res = session.get(a['href'], timeout=12)
                    p_soup = BeautifulSoup(p_res.text, 'html.parser')
                    gallery = p_soup.find_all(class_=re.compile(r'woocommerce-product-gallery|product-gallery|gallery', re.I))
                    for g in gallery:
                        for ga in g.find_all('a', href=True):
                            if any(ext in ga['href'].lower() for ext in ['.jpg', '.png', '.webp']):
                                u_clean = re.sub(r'-\d+x\d+(\.[a-zA-Z0-9]+)$', r'\1', ga['href'])
                                if u_clean not in candidate_urls:
                                    candidate_urls.append(u_clean)
                    break
    except Exception as e:
        print(f"Odorem DZ search note: {e}")

    print(f"Found {len(candidate_urls)} candidate Guerlain L'Homme Idéal Extrême photos:")
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

    print(f"Done! Successfully saved {saved} authentic Guerlain L'Homme Idéal Extrême photos into GUERLAIN L'HOMME IDEAL EXTREME EDP 100ML/")

if __name__ == '__main__':
    fetch_guerlain_extreme()
