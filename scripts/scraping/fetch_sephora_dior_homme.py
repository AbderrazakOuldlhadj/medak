import os
import sys
import time
from PIL import Image
from playwright.sync_api import sync_playwright

sys.path.append(os.path.join(r'c:\Users\msipc\Desktop\products\parfums', 'scripts', 'processing'))
from process_image_assets import format_image_to_square_webp

sys.stdout.reconfigure(encoding='utf-8')

def download_sephora_dior_homme():
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
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
        page = context.new_page()

        print("Navigating to Sephora search for Dior Homme Intense...")
        page.goto('https://www.sephora.fr/recherche?q=Dior+Homme+Intense', wait_until='domcontentloaded', timeout=30000)
        time.sleep(3)

        # Accept cookie banner
        for selector in ['#onetrust-accept-btn-handler', 'button:has-text("Tout accepter")', '#footer_tc_privacy_button_2', 'button:has-text("Accepter")']:
            try:
                btn = page.locator(selector).first
                if btn.is_visible():
                    btn.click()
                    time.sleep(1)
                    break
            except Exception:
                pass

        cards = page.locator('a.product-tile-link, a[data-product-id], div.product-tile a').all()
        if cards:
            print(f"Found {len(cards)} product cards. Clicking item...")
            cards[0].click()
            time.sleep(4)
            print(f"Product page URL: {page.url}")

            img_urls = page.eval_on_selector_all(
                'img',
                'elements => elements.map(e => e.src || e.getAttribute("data-src") || "").filter(s => s)'
            )

            sephora_imgs = []
            for u in img_urls:
                if 'media.sephora.eu' in u or 'demandware.static' in u:
                    if any(k in u for k in ['media_principal', 'media_', 'published', 'PIM', 'massivpimupload', '53514', 'Dior']):
                        base_u = u.split('?')[0]
                        high_res = f"{base_u}?scaleWidth=1000&scaleMode=fit"
                        if high_res not in sephora_imgs:
                            sephora_imgs.append(high_res)

            if not sephora_imgs:
                sephora_imgs = [
                    'https://media.sephora.eu/PIM/53514_main.jpg?scaleWidth=1000&scaleMode=fit',
                    'https://media.sephora.eu/PIM/53514_1.jpg?scaleWidth=1000&scaleMode=fit',
                    'https://media.sephora.eu/PIM/53514_2.jpg?scaleWidth=1000&scaleMode=fit'
                ]

            print(f"Found {len(sephora_imgs)} Sephora authentic product photos:")
            for si in sephora_imgs:
                print("  ->", si)

            saved = 0
            for idx, iu in enumerate(sephora_imgs[:5], 1):
                try:
                    resp = page.goto(iu, wait_until='networkidle', timeout=15000)
                    if resp and resp.status == 200:
                        body = resp.body()
                        if len(body) > 5000:
                            raw_name = f'raw_{idx}.jpg'
                            raw_path = os.path.join(target_dir, raw_name)
                            with open(raw_path, 'wb') as f:
                                f.write(body)

                            img = Image.open(raw_path)
                            webp_name = 'bottle.webp' if idx == 1 else f'image_{idx}.webp'
                            webp_path = os.path.join(target_dir, webp_name)
                            success = format_image_to_square_webp(img, webp_path, remove_bg=True)
                            if success:
                                print(f'  [✓ Downloaded & Processed] {raw_name} -> {webp_name} ({img.width}x{img.height}px, {len(body)//1024} KB)')
                                saved += 1
                except Exception as e:
                    print(f'  Error page.goto({iu}): {e}')
        else:
            print("No product cards found.")

        browser.close()

if __name__ == '__main__':
    download_sephora_dior_homme()
