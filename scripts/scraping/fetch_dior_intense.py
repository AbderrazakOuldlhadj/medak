import os
import sys
import time
from PIL import Image
from playwright.sync_api import sync_playwright

sys.path.append(os.path.join(r'c:\Users\msipc\Desktop\products\parfums', 'scripts', 'processing'))
from process_image_assets import format_image_to_square_webp

sys.stdout.reconfigure(encoding='utf-8')

def fetch_dior_intense_search():
    target_dir = r'c:\Users\msipc\Desktop\products\parfums\assets\product_images\DIOR HOMME INTENSE EDP 150ML'
    os.makedirs(target_dir, exist_ok=True)

    # Clean out directory first
    for f in os.listdir(target_dir):
        fp = os.path.join(target_dir, f)
        if os.path.isfile(fp):
            try: os.remove(fp)
            except Exception: pass

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=['--disable-blink-features=AutomationControlled'])
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        page = context.new_page()

        print("Navigating to Google search...")
        page.goto('https://www.google.com/search?q=site:sephora.fr+dior+homme+intense+P53514', wait_until='domcontentloaded', timeout=30000)
        time.sleep(2)

        links = page.locator('a').all()
        target_link = None
        for l in links:
            try:
                href = l.get_attribute('href') or ''
                if 'sephora.fr/p/dior-homme-intense' in href or 'P53514' in href:
                    target_link = l
                    print(f"Found Sephora link in Google: {href}")
                    break
            except Exception:
                pass

        if target_link:
            target_link.click()
            time.sleep(4)
            print(f"Navigated to Sephora page title: {page.title()}")

            img_urls = page.eval_on_selector_all(
                'img',
                'elements => elements.map(e => e.src || e.getAttribute("data-src") || "").filter(s => s)'
            )
            sephora_imgs = []
            for u in img_urls:
                if 'media.sephora.eu' in u or 'demandware.static' in u:
                    base_u = u.split('?')[0]
                    high_res = f"{base_u}?scaleWidth=1000&scaleMode=fit"
                    if high_res not in sephora_imgs:
                        sephora_imgs.append(high_res)

            print(f"Found {len(sephora_imgs)} Sephora authentic product photos:")
            for si in sephora_imgs:
                print("  ->", si)

            saved = 0
            for idx, iu in enumerate(sephora_imgs, 1):
                try:
                    res = page.request.get(iu)
                    if res.status == 200:
                        raw_name = f'raw_{idx}.jpg'
                        raw_path = os.path.join(target_dir, raw_name)
                        with open(raw_path, 'wb') as f:
                            f.write(res.body())

                        img = Image.open(raw_path)
                        webp_name = 'bottle.webp' if idx == 1 else f'image_{idx}.webp'
                        webp_path = os.path.join(target_dir, webp_name)
                        success = format_image_to_square_webp(img, webp_path, remove_bg=True)
                        if success:
                            print(f'  [✓ Saved Sephora Photo {idx}] {raw_name} -> {webp_name} ({img.width}x{img.height}px, {len(res.body())//1024} KB)')
                            saved += 1
                except Exception as e:
                    print(f'  Error {iu}: {e}')
        else:
            print("No matching Sephora link found on Google search.")

        browser.close()

if __name__ == '__main__':
    fetch_dior_intense_search()
