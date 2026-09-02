import os
import sys
import time
from PIL import Image
from playwright.sync_api import sync_playwright

sys.path.append(os.path.join(r'c:\Users\msipc\Desktop\products\parfums', 'scripts', 'processing'))
from process_image_assets import format_image_to_square_webp

sys.stdout.reconfigure(encoding='utf-8')

def fetch_clinique_sephora():
    target_dir = r'c:\Users\msipc\Desktop\products\parfums\assets\product_images\CLINIQUE HAPPY COLOGNE FOR MEN EDT 100ML'
    os.makedirs(target_dir, exist_ok=True)

    # Clean out old bad files
    for f in os.listdir(target_dir):
        fp = os.path.join(target_dir, f)
        if os.path.isfile(fp):
            try: os.remove(fp)
            except Exception: pass

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=['--disable-blink-features=AutomationControlled'])
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        page = context.new_page()

        print("Navigating to Sephora FR search for Clinique Happy For Men...")
        page.goto('https://www.sephora.fr/recherche?q=Clinique+Happy+For+Men', wait_until='domcontentloaded', timeout=30000)
        time.sleep(3)

        # Accept cookies if popup appears
        try:
            cookie_btn = page.locator('#footer_tc_privacy_button_2, button:has-text("Accepter"), #onetrust-accept-btn-handler')
            if cookie_btn.first.is_visible():
                cookie_btn.first.click()
                time.sleep(1)
        except Exception:
            pass

        cards = page.locator('a.product-tile-link, a[data-product-id]').all()
        if cards:
            print(f"Found {len(cards)} product cards. Clicking first matching item...")
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
                    if any(k in u for k in ['media_principal', 'media_', 'published', 'PIM', 'massivpimupload', 'Clinique', 'happy']):
                        base_u = u.split('?')[0]
                        high_res = f"{base_u}?scaleWidth=1000&scaleMode=fit"
                        if high_res not in sephora_imgs:
                            sephora_imgs.append(high_res)

            print(f"Found {len(sephora_imgs)} Sephora FR authentic product photos:")
            for s_img in sephora_imgs:
                print("  ->", s_img)

            saved = 0
            for idx, iu in enumerate(sephora_imgs[:5], 1):
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
                            print(f'  [✓ Saved Authentic Photo {idx}] {raw_name} -> {webp_name} ({img.width}x{img.height}px, {len(res.body())//1024} KB)')
                            saved += 1
                except Exception as e:
                    print(f'  Error saving {iu}: {e}')
        else:
            print("No product cards found.")

        browser.close()

if __name__ == '__main__':
    fetch_clinique_sephora()
