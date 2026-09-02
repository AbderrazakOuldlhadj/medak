import os
import sys
import time
from PIL import Image
from playwright.sync_api import sync_playwright

sys.path.append(os.path.join(r'c:\Users\msipc\Desktop\products\parfums', 'scripts', 'processing'))
from process_image_assets import format_image_to_square_webp

sys.stdout.reconfigure(encoding='utf-8')

def screenshot_dior():
    target_dir = r'c:\Users\msipc\Desktop\products\parfums\assets\product_images\DIOR HOMME INTENSE EDP 150ML'
    os.makedirs(target_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=['--disable-blink-features=AutomationControlled'])
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
        page = context.new_page()

        print("Navigating to Sephora FR Dior Homme Intense product page...")
        page.goto('https://www.sephora.fr/p/dior-homme-intense---eau-de-parfum-intense-P53514.html', wait_until='commit', timeout=20000)
        time.sleep(5)

        print(f"Page title: {page.title()}")

        # Accept cookie banner if present
        for selector in ['#onetrust-accept-btn-handler', 'button:has-text("Tout accepter")']:
            try:
                btn = page.locator(selector).first
                if btn.is_visible():
                    btn.click()
                    time.sleep(1)
                    break
            except Exception:
                pass

        imgs = page.locator('img[src*="53514"], img[src*="media.sephora"], div.product-cover img, .product-media img').all()
        print(f"Found {len(imgs)} candidate image elements in DOM.")

        saved = 0
        for idx, img_el in enumerate(imgs[:4], 1):
            try:
                if img_el.is_visible():
                    raw_name = f'raw_{idx}.jpg'
                    raw_path = os.path.join(target_dir, raw_name)
                    img_el.screenshot(path=raw_path)
                    
                    img = Image.open(raw_path)
                    if img.width > 100 and img.height > 100:
                        webp_name = 'bottle.webp' if saved == 0 else f'image_{saved+1}.webp'
                        webp_path = os.path.join(target_dir, webp_name)
                        success = format_image_to_square_webp(img, webp_path, remove_bg=True)
                        if success:
                            print(f'  [✓ Screenshot Saved & Processed] {raw_name} -> {webp_name} ({img.width}x{img.height}px)')
                            saved += 1
            except Exception as e:
                print(f'  Error capturing screenshot: {e}')

        browser.close()

if __name__ == '__main__':
    screenshot_dior()
