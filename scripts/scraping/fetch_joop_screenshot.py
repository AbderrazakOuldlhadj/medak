import os
import sys
import time
from PIL import Image
from playwright.sync_api import sync_playwright

sys.path.append(os.path.join(r'c:\Users\msipc\Desktop\products\parfums', 'scripts', 'processing'))
from process_image_assets import format_image_to_square_webp

sys.stdout.reconfigure(encoding='utf-8')

def fetch_joop_screenshot():
    target_dir = r'c:\Users\msipc\Desktop\products\parfums\assets\product_images\JOOP HOMME EDT 125ML'
    os.makedirs(target_dir, exist_ok=True)

    url = 'https://www.nocibe.fr/fr/p/1011105304?variant=611467'

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=['--disable-blink-features=AutomationControlled'])
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
        page = context.new_page()

        print(f"Navigating to Nocibé URL: {url}")
        try:
            page.goto(url, wait_until='domcontentloaded', timeout=25000)
            time.sleep(4)
        except Exception as e:
            print(f"Nav note: {e}")

        for selector in ['#onetrust-accept-btn-handler', 'button:has-text("Tout accepter")', 'button:has-text("Accepter")']:
            try:
                btn = page.locator(selector).first
                if btn.is_visible():
                    btn.click()
                    time.sleep(1)
                    break
            except Exception:
                pass

        imgs = page.locator('img[src*="611467"], img[src*="medias"], .product-media img, div[class*="gallery"] img').all()
        print(f"DOM image elements found: {len(imgs)}")

        saved = 0
        for idx, img_el in enumerate(imgs[:6], 1):
            try:
                if img_el.is_visible():
                    raw_name = f'raw_{saved+1}.jpg'
                    raw_path = os.path.join(target_dir, raw_name)
                    img_el.screenshot(path=raw_path)

                    img = Image.open(raw_path)
                    if img.width >= 100 and img.height >= 100:
                        webp_name = 'bottle.webp' if saved == 0 else f'image_{saved+1}.webp'
                        webp_path = os.path.join(target_dir, webp_name)
                        success = format_image_to_square_webp(img, webp_path, remove_bg=True)
                        if success:
                            print(f'  [✓ Screenshot Saved & Processed] {raw_name} -> {webp_name} ({img.width}x{img.height}px)')
                            saved += 1
            except Exception as e:
                print(f'  Error capturing screenshot: {e}')

        browser.close()

    print(f"Done! Saved {saved} authentic Joop! Homme EDT 125ml photos into JOOP HOMME EDT 125ML/")

if __name__ == '__main__':
    fetch_joop_screenshot()
